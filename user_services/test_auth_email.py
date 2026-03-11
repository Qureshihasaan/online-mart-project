import sys
import os
sys.path.append(os.getcwd())
import unittest
from sqlmodel import Session, SQLModel, create_engine, select
from user_services.model import User, CreateUser
from user_services.schema import authenticate_user, bcrypt_context
from user_services.utils import create_access_token, decode_access_token
from datetime import timedelta

class TestAuthEmail(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        
        # Create a test user
        self.test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=bcrypt_context.hash("testpassword"),
            role="buyer"
        )
        self.session.add(self.test_user)
        self.session.commit()

    def test_authenticate_user_with_email(self):
        # Test successful authentication with email
        user = authenticate_user("test@example.com", "testpassword", self.session)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")

        # Test failed authentication with wrong password
        user = authenticate_user("test@example.com", "wrongpassword", self.session)
        self.assertFalse(user)

        # Test failed authentication with username (should fail now)
        user = authenticate_user("testuser", "testpassword", self.session)
        self.assertFalse(user)

    def test_create_access_token_with_email(self):
        token = create_access_token(
            email="test@example.com",
            user_id=1,
            role="buyer",
            expires_delta=timedelta(minutes=10)
        )
        decoded = decode_access_token(token)
        self.assertEqual(decoded["sub"], "test@example.com")
        self.assertEqual(decoded["role"], "buyer")

if __name__ == "__main__":
    unittest.main()
