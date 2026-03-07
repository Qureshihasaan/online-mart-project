from datetime import datetime , timedelta
from jose import jwt
from typing import Optional
from . import setting


def create_access_token(username : str , user_id : int , expires_delta : timedelta):
    encode = {"sub" : username, "id" : user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp" : expires})
    return jwt.encode(encode, setting.SECRET_KEY, algorithm=setting.ALGORITHM)


def decode_access_token(access_token : str):
    decoded_jwt = jwt.decode(access_token , setting.SECRET_KEY , algorithms=[setting.ALGORITHM])
    return decoded_jwt



def verify_access_token(token:str):
    payload = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
    return payload
    