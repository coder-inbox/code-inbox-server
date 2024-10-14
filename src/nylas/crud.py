"""📧 Nylas CRUD Module 📦

This module provides CRUD (Create, Read, Update, Delete) operations for Nylas and user-related data.

Dependencies:
    - bson: ObjectId manipulation.
    - datetime: Date and time handling.
    - fastapi.encoders: JSON encoding.
    - odmantic.session: Database session.
    - pydantic: Data validation.
    - typing: Type hints.
    - os: Operating System.
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

from bson import (
    ObjectId,
)
from datetime import (
    datetime,
)
from fastapi.encoders import (
    jsonable_encoder,
)
from odmantic.session import (
    AIOSession,
)
import os
from pydantic import (
    EmailStr,
)
from typing import (
    Any,
    Dict,
    Optional,
)

from src.config import (
    settings,
)
from src.nylas import (
    models as nylas_models,
)
from src.users import (
    models as users_models,
    schemas as users_schemas,
)


async def create_user(
    email: EmailStr, session: AIOSession
) -> Optional[users_models.User]:
    """
    A method to insert a user into the users table.

    Args:
        email (EmailStr): A user's email address.
        session (AIOSession): Odmantic session object.

    Returns:
        users_models.User: A User model instance.
    """
    try:
        from src.main import (
            code_app,
        )

        full_name = code_app.state.nylas.account.get("name")
        user = users_models.User(full_name=full_name, email=email)
        await session.save(user)
        return user
    except Exception as e:
        print(f"Error creating user: {e}")
        return None


async def find_existed_user(
    email: EmailStr, session: AIOSession
) -> users_models.User:
    """
    A method to fetch user info given an email.

    Args:
        email (EmailStr): A given user email.
        session (AIOSession): Odmantic session object.

    Returns:
        Optional[users_models.User]: The current user object, if found.
    """
    user = await session.find_one(
        users_models.User, users_models.User.email == email
    )
    return user


async def find_existed_user_id(
    user_id: str, session: AIOSession
) -> users_schemas.UserObjectSchema:
    """
    A method to fetch user info given an ID.

    Args:
        user_id (str): A given user ID.
        session (AIOSession): Odmantic session object.

    Returns:
        Optional[users_schemas.UserObjectSchema]: The current user object, if found.
    """
    user = await session.find_one(
        users_models.User, users_models.User.id == ObjectId(user_id)
    )
    return users_schemas.UserObjectSchema(**jsonable_encoder(user))


async def login_user(token: str, session: AIOSession) -> Dict[str, Any]:
    """
    A method to fetch and return serialized user info upon logging in.

    Args:
        token (str): Nylas code.
        session (AIOSession): Odmantic session object.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'status_code' (int): HTTP status code.
            - 'message' (str): A welcome message.
            - 'user' (Dict[str, Any]): User information.
            - 'token' (str): Access token.
    """
    from src.main import (
        code_app,
    )

    access_token_obj = code_app.state.nylas.send_authorization(token)
    access_token = access_token_obj["access_token"]
    email_address = access_token_obj["email_address"]

    user_obj = await find_existed_user(email_address, session)

    if not user_obj:
        await create_user(email_address, session)
        del user_obj

    user_obj = await find_existed_user(email_address, session)

    find_token = await session.find_one(
        nylas_models.AccessToken,
        nylas_models.AccessToken.user == user_obj.id,
    )

    if not find_token:
        find_token = nylas_models.AccessToken(
            user=user_obj.id,
            tokens=[access_token],
        )
    else:
        tokens = find_token.tokens
        tokens.extend([access_token])
        find_token.update(
            {
                "user": user_obj.id,
                "tokens": tokens,
                "modified_date": datetime.utcnow(),
            }
        )
    await session.save(find_token)
    return {
        "status_code": 200,
        "message": "Welcome back!",
        "user": jsonable_encoder(user_obj),
        "token": access_token,
    }


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
        except Exception as e:
            print(f"Error finding token: {e}")
        return None
    except Exception as e:
        print(f"Error finding token: {e}")
        return None


async def send_welcome_email(to: str) -> None:
    """
    Send a welcome email to a specified recipient.

    Args:
        to (str): The email address of the recipient.

    This function sends a welcome email to a specified recipient using the Nylas API.
    The email content is read from a static HTML file located in the "static" directory.

    The email subject is set to "Welcome to Code Inbox 🚀", and the sender's email address
    is retrieved from the Nylas account settings.

    Note:
    - Ensure that the HTML file for the welcome email is located in the "static" directory
      and named "welcome_email.html".
    - This function does not handle errors or exceptions related to sending the email.

    Example:
        send_welcome_email("user@example.com")
    """
    from src.main import (
        code_app,
    )

    # Store the initial access token
    initial_token = code_app.state.nylas.access_token

    # Set the Nylas access token to the system token
    code_app.state.nylas.access_token = settings().NYLAS_SYSTEM_TOKEN

    # Create a draft email
    draft = code_app.state.nylas.drafts.create()

    # Read the HTML content of the welcome email from a file
    with open(
        os.path.join(os.getcwd(), "static", "welcome_email.html"),
        "r",
        encoding="utf-8",
    ) as file:
        html_content = file.read()

    # Set the email subject
    draft["subject"] = "Welcome to Code Inbox 🚀"

    # Set the recipient's email address
    draft["to"] = [{"email": to}]

    # Set the email body to the HTML content
    draft["body"] = html_content

    # Set the sender's email address from the Nylas account
    draft["from"] = [{"email": code_app.state.nylas.account.email_address}]

    # TODO: use draft.send_raw ???
    draft.send()

    # Restore the initial access token
    code_app.state.nylas.access_token = initial_token
