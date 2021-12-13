import bcrypt
import re
import uuid
from api.exceptions import BadRequest, InvalidEmail, InvalidPassword, UserAlreadyExists, UserNotVerified, UserNotFound, InvalidCredentials
from config import Config
from datetime import datetime, timedelta
from flask_jwt_extended import (create_access_token,  get_jwt_identity)
from infrastructure.database_repository import DatabaseRepository

config = Config()


class Auth:
    def __init__(self, db, email_service):
        self._db = db
        self._email_service = email_service

    def register(self, request_data):
        email = request_data.get('email')
        password = request_data.get('password')

        # Validate email and password
        if not Auth.is_email_valid(email):
            raise InvalidEmail('Invalid email address.')

        if not Auth.is_password_format_valid(password):
            raise InvalidPassword(
                'The password must be between 8 and 60 characters long.')

        # Check if the user already exists, if so raise an exception
        user = self._db.get_user_by_email(email)
        if user:
            raise UserAlreadyExists(
                'A user account with this email address already exists.')

        # Create the user account
        hashed_password = Auth.hash_password(password)
        user = self._db.create_user(email, hashed_password)

        # Create an access token
        access_token = Auth.generate_access_token_for_user(user.email)

        return access_token, user

    def login(self, request_data):
        # Accept an email and password
        email = request_data.get('email')
        password = request_data.get('password')

        # Look up the user by email
        user = self._db.get_user_by_email(email)
        if not user:
            raise UserNotFound('Invalid email address.')

        # Verify that the user's password is correct
        if not Auth.check_password(password, user.hashed_password):
            raise InvalidCredentials('Invalid email address or password.')

        # Ensure that the email is verified
        # if config.is_production() and not user.verified_at:
        #     raise UserNotVerified('This email address has not been verified.')

        # Create an access token
        access_token = Auth.generate_access_token_for_user(user.email)

        return access_token, user

    def verify(self, request_data):
        token = request_data.get('token')

        # Validate the token
        if not token:
            raise BadRequest('A token is required.')

        user = self._db.get_user_by_token(token)
        if not user:
            raise BadRequest('Invalid token.')

        # Ensure that the token hasn't expired
        token_exp = user.verification_token_expiration
        exp = datetime.fromisoformat(token_exp.isoformat())
        if exp < datetime.now():
            raise BadRequest('The token has expired.')

        # Verify the user
        self._db.verify_user(user.id)

        # Create an access token
        access_token = Auth.generate_access_token_for_user(user.email)

        return access_token, user

    def init_password_reset(self, email):
        user = self._db.get_user_by_email(email)
        if not user:
            raise UserNotFound('Invalid email address.')

        # Generate a token
        token, exp = Auth.generate_reset_token()
        self._db.set_reset_token_for_user(user.id, token, exp)

        # Send a reset email
        self._email_service.send_reset_email(user.email, token)

    def reset_password(self, token, new_password):
        # Lookup the token
        user = self._db.get_user_by_reset_token(token)
        if not user:
            raise BadRequest('Invalid token.')

        # Ensure that the token hasn't expired
        token_exp = user.reset_token_expiration
        exp = datetime.fromisoformat(token_exp.isoformat())
        if exp < datetime.now():
            raise BadRequest('The token has expired.')

        # Update the user's password
        if not Auth.is_password_format_valid(new_password):
            raise InvalidPassword(
                'The password must be between 8 and 60 characters long.')

        hashed_password = Auth.hash_password(new_password)
        self._db.update_password(user.id, hashed_password)

        # Create an access token
        access_token = Auth.generate_access_token_for_user(user.email)

        return access_token, user

    def current_user(self):
        email = Auth.identity()
        if not email:
            return None

        return self._db.get_user_by_email(email)

    @staticmethod
    def is_email_valid(email):
        if not email:
            return False

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False

        return True

    @staticmethod
    def is_password_format_valid(password):
        if not password:
            return False

        if len(password) < 8 or len(password) > 60:
            return False

        return True

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def check_password(password, hashed_password):
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

    @staticmethod
    def generate_access_token_for_user(email):
        expires = timedelta(days=365)
        return create_access_token(email, expires_delta=expires)

    @staticmethod
    def generate_verification_token():
        token = uuid.uuid4()
        expiration = datetime.now() + timedelta(days=7)
        return str(token), expiration

    @staticmethod
    def generate_reset_token():
        token = uuid.uuid4()
        expiration = datetime.now() + timedelta(hours=1)
        return str(token), expiration

    @staticmethod
    def identity():
        return get_jwt_identity()
