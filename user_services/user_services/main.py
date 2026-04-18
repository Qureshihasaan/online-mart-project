from contextlib import asynccontextmanager
from aiokafka import AIOKafkaProducer
from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from typing import AsyncGenerator, Annotated, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .schema import bcrypt_context, authenticate_user
from .consumer import consume
from .producer import kafka_producer
from .database import create_db_and_tables, get_session
import asyncio, json
from .model import User, CreateUser, Token, GoogleAuthRequest
from sqlmodel import Session, select
from . import setting
from fastapi.middleware.cors import CORSMiddleware
from .utils import create_access_token, decode_access_token
from .role_checker import require_role
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating Tables...")
    task = asyncio.create_task(consume())
    create_db_and_tables()
    yield


app: FastAPI = FastAPI(lifespan=lifespan, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@app.post("/Signup", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: CreateUser,
    db: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)],
) -> dict:
    if not user.username or not user.plain_password:
        raise HTTPException(status_code=400, detail="Please Enter Username or Password....")

    # Validate role
    if user.role not in ("buyer", "seller", "admin"):
        raise HTTPException(status_code=400, detail="Role must be 'buyer', 'seller', or 'admin'")

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=bcrypt_context.hash(user.plain_password),
        role=user.role,
        auth_provider="local",
    )
    db.add(new_user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="User Already Exists...")

    event = {
        "event_type": "User_Created",
        "user": {
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
    }
    await producer.send_and_wait(setting.KAFKA_USER_TOPIC, json.dumps(event).encode("utf-8"))
    print("User_data sent to kafka topic...")
    return {"message": "User Account Created Successfully"}


@app.post("/login", response_model=Token)
async def login_with_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_session)],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could Not Validate User")
    access_token = create_access_token(
        user.username,
        user.id,
        user.role,
        timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/google", response_model=Token)
async def google_auth(
    request: GoogleAuthRequest,
    db: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)],
) -> Token:
    """
    Google OAuth login/signup:
    1. Verify the Google ID token
    2. If user exists → login
    3. If user doesn't exist → auto-create with role='buyer'
    4. Return JWT access token
    """
    try:
        # Verify the Google ID token
        print(f"Verifying Google token with client_id: {str(setting.GOOGLE_CLIENT_ID)}")
        idinfo = id_token.verify_oauth2_token(
            request.id_token,
            google_requests.Request(),
            str(setting.GOOGLE_CLIENT_ID),
        )
        print(f"Token verified successfully: {idinfo.get('email')}")
    except ValueError as e:
        print(f"Google token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid Google ID token")

    google_id = idinfo["sub"]
    email = idinfo.get("email", "")
    name = idinfo.get("name", email.split("@")[0])

    # Check if user already exists (by google_id or email)
    user = db.exec(select(User).where(User.google_id == google_id)).first()
    if not user:
        user = db.exec(select(User).where(User.email == email)).first()

    if user:
        # Existing user — link Google account if not already linked
        if not user.google_id:
            user.google_id = google_id
            user.auth_provider = "google"
            db.add(user)
            db.commit()
            db.refresh(user)
    else:
        # New user — auto-create
        user = User(
            username=name,
            email=email,
            hashed_password=None,
            role="buyer",
            auth_provider="google",
            google_id=google_id,
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            raise HTTPException(status_code=400, detail="Could not create user")

        # Publish user created event
        event = {
            "event_type": "User_Created",
            "user": {
                "username": name,
                "email": email,
                "role": "buyer",
                "auth_provider": "google",
            },
        }
        await producer.send_and_wait(setting.KAFKA_USER_TOPIC, json.dumps(event).encode("utf-8"))
        print("Google user created and sent to kafka topic...")

    # Generate JWT
    access_token = create_access_token(
        user.email,
        user.id,
        user.role,
        timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/get_access_token")
def get_access_token(email: str, role: str = "buyer", user_id: Optional[int] = None):
    access_token_expire = timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(email, user_id, role, expires_delta=access_token_expire)
    return {"access_token": access_token}


@app.get("/decode_token")
def decode_token(access_token: str):
    try:
        decoded = decode_access_token(access_token)
        return {"decode_token": decoded}
    except Exception as e:
        return {"error": str(e)}


@app.get("/user/all")
def get_all_user(db: Annotated[Session, Depends(get_session)]):
    users = db.exec(select(User)).all()
    return users


@app.get("/user/me")
def read_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_session)]):
    user_token_data = decode_access_token(token)
    user = db.exec(select(User).where(User.email == user_token_data["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/user/{user_id}")
async def get_user_details(
    user_id: int,
    db: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    user_token_data = decode_access_token(token)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/user/delete/{user_id}")
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_session)]):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User Deleted Successfully"}