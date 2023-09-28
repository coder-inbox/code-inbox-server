"""📧 Nylas CRUD Module 📦

This module provides CRUD (Create, Read, Update, Delete) operations for Nylas and user-related data.

Dependencies:
    - bson: ObjectId manipulation.
    - datetime: Date and time handling.
    - fastapi.encoders: JSON encoding.
    - odmantic.session: Database session.
    - pydantic: Data validation.
    - typing: Type hints.
    - src.nylas.models: Nylas data models.
    - src.nylas.schemas: Nylas data schemas.
    - src.users.models: User data models.
    - src.users.schemas: User data schemas.

Functions:
    create_user: Insert a user into the users table.
    find_existed_user: Fetch user info given an email.
    find_existed_user_id: Fetch user info given an ID.
    login_user: Fetch and return serialized user info upon logging in.
    find_existed_token: Find a token in a token list.
"""
from bson import ObjectId
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
from odmantic.session import AIOSession
from pydantic import EmailStr
from typing import Any, Dict, Optional, Union, List
from src.nylas import models as nylas_models, schemas as nylas_schemas
from src.users import models as users_models, schemas as users_schemas

async def create_user(
    email: EmailStr, session: AIOSession
) -> users_models.User:
    """
    A method to insert a user into the users table.

    Args:
        email (EmailStr): A user's email address.
        session (AIOSession): Odmantic session object.

    Returns:
        users_models.User: A User model instance.
    """
    try:
        from src.main import code_app
        full_name = code_app.state.nylas.account.get("name")
        user = users_models.User(full_name=full_name, email=email)
        await session.save(user)
        return user
    except Exception as e:
        print(f"Error creating user: {e}")

async def find_existed_user(
    email: EmailStr, session: AIOSession
) -> Optional[users_models.User]:
    """
    A method to fetch user info given an email.

    Args:
        email (EmailStr): A given user email.
        session (AIOSession): Odmantic session object.

    Returns:
        Optional[users_models.User]: The current user object, if found.
    """
    try:
        user = await session.find_one(
            users_models.User, users_models.User.email == email
        )
        return user
    except Exception as e:
        print(f"Error finding user: {e}")

async def find_existed_user_id(
    user_id: str, session: AIOSession
) -> Optional[users_schemas.UserObjectSchema]:
    """
    A method to fetch user info given an ID.

    Args:
        user_id (str): A given user ID.
        session (AIOSession): Odmantic session object.

    Returns:
        Optional[users_schemas.UserObjectSchema]: The current user object, if found.
    """
    try:
        user = await session.find_one(
            users_models.User, users_models.User.id == ObjectId(user_id)
        )
        if user:
            return users_schemas.UserObjectSchema(**jsonable_encoder(user))
        return None
    except Exception as e:
        print(f"Error finding user by ID: {e}")

async def login_user(
    token: str, session: AIOSession
) -> Dict[str, Union[int, str, Dict[str, Any], str]]:
    """
    A method to fetch and return serialized user info upon logging in.

    Args:
        token (str): Nylas code.
        session (AIOSession): Odmantic session object.

    Returns:
        Dict[str, Union[int, str, Dict[str, Any], str]]: A dictionary containing:
            - 'status_code' (int): HTTP status code.
            - 'message' (str): A welcome message.
            - 'user' (Dict[str, Any]): User information.
            - 'token' (str): Access token.
    """
    try:
        from src.main import code_app

        access_token_obj = code_app.state.nylas.send_authorization(token)
        access_token = access_token_obj['access_token']
        email_address = access_token_obj['email_address']

        user_obj = await find_existed_user(email_address, session)
        print(user_obj)

        if not user_obj:
            await create_user(email_address, session)
            del user_obj

        user_obj = await find_existed_user(email_address, session)

        token = await session.find_one(
            nylas_models.AccessToken, nylas_models.AccessToken.user == user_obj.id
        )

        if not token:
            token = nylas_models.AccessToken(
                user=user_obj.id,
                tokens=[access_token],
            )
        else:
            tokens = token.tokens
            tokens.extend([access_token])
            token.update(
                {
                    "user": user_obj.id,
                    "tokens": tokens,
                    "modified_date": datetime.utcnow(),
                }
            )
        await session.save(token)
        return {"status_code": 200, "message": "Welcome back!", "user": jsonable_encoder(user_obj), "token": access_token}
    except Exception as e:
        print(f"Error logging in user: {e}")

async def find_existed_token(
    email: EmailStr, token: str, session: AIOSession
) -> Optional[Any]:
    """
    A method for finding a token in a token list.

    Args:
        email (EmailStr): An email address of an authenticated user.
        token (str): A token value.
        session (AIOSession): Odmantic session object.

    Returns:
        Optional[Any]: The user object if the token is found, otherwise None.
    """
    try:
        user = await find_existed_user(email, session)
        token_obj = await session.find_one(
            nylas_models.AccessToken, nylas_models.AccessToken.user == user.id
        )
        try:
            tokens = token_obj.tokens
            if token in tokens:
                return user
        except Exception:
            print(f"Error finding token: {e}")
        return None
    except Exception as e:
        print(f"Error finding token: {e}")
        return None
