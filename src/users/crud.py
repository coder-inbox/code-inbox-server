"""🛠️ Users CRUD Module 📦

This module contains functions for performing CRUD (Create, Read, Update, Delete)
operations related to user data.

Functions:
    - remove_token(user_id: ObjectId, token: str, session: AIOSession)
        -> None: Remove a token from a user's token list.
    - update_profile_picture(email: EmailStr, file_name: str, session: AIOSession)
        -> None: Update a user's profile picture.
    - update_user_info(personal_info: users_schemas.PersonalInfo, current_user:
        users_schemas.UserObjectSchema, session: AIOSession) -> None: Update a user's personal information.

Dependencies:
    - bson.ObjectId: For working with MongoDB ObjectIds.
    - datetime: For handling date and time.
    - odmantic.session.AIOSession: For asynchronous database sessions.
    - pydantic.EmailStr: For validating email addresses.

External Dependencies:
    - src.nylas.crud: CRUD operations related to Nylas access tokens.
    - src.nylas.models: Nylas-related data models.
    - src.users.models: User-related data models.
    - src.users.schemas: User-related Pydantic schemas.

"""

from bson import (
    ObjectId,
)
from datetime import (
    datetime,
)
from odmantic.session import (
    AIOSession,
)
from pydantic import (
    EmailStr,
)

from src.nylas import (
    models as nylas_models,
)
from src.users import (
    models as users_models,
    schemas as users_schemas,
)


async def remove_token(
    user_id: ObjectId, token: str, session: AIOSession
) -> None:
    """Remove Token

    Remove a token from a user's token list.

    Args:
        user_id (ObjectId): User's ObjectId.
        token (str): Token value to be removed.
        session (AIOSession): An odmantic session object.
    """
    token_obj = await session.find_one(
        nylas_models.AccessToken, nylas_models.AccessToken.user == user_id
    )
    tokens = token_obj.tokens
    if token in tokens:
        tokens.remove(token)
        token_obj.update(
            {
                "user": user_id,
                "tokens": tokens,
                "modified_date": datetime.utcnow(),
            }
        )
        await session.save(token_obj)


async def update_profile_picture(
    email: EmailStr, file_name: str, session: AIOSession
) -> None:
    """Update Profile Picture

    Update a user's profile picture.

    Args:
        email (EmailStr): User's email address.
        file_name (str): Relative image file path stored on a Deta drive.
        session (AIOSession): An odmantic session object.
    """
    user = await session.find_one(
        users_models.User, users_models.User.email == email
    )
    user.profile_picture = file_name
    await session.save(user)


async def update_user_info(
    personal_info: users_schemas.PersonalInfo,
    current_user: users_schemas.UserObjectSchema,
    session: AIOSession,
) -> None:
    """Update User Info

    Update a user's personal information.

    Args:
        personal_info (PersonalInfo): User's personal info schema object.
        current_user (UserObjectSchema): User schema object.
        session (AIOSession): An odmantic session object.
    """
    current_user.update(
        {
            "full_name": personal_info.full_name,
            "bio": personal_info.bio,
            "programming_language": personal_info.programming_language,
            "modified_date": datetime.utcnow(),
        }
    )
    await session.save(current_user)
