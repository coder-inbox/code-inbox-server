"""📜 Users Schemas Module 📦

This module defines Pydantic schemas for representing user data.

Schemas:
    - UserObjectSchema (BaseModel): User schema for fetching user info.
    - PersonalInfo (BaseModel): User schema for updating user info.

Attributes:
    - datetime: For handling date and time.
    - pydantic.BaseModel: For defining Pydantic models.
    - pydantic.EmailStr: For validating email addresses.
    - pydantic.Field: For defining model fields.
    - typing: For type hints and annotations.

"""

from datetime import (
    datetime,
)
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)
from typing import (
    Optional,
)


class UserObjectSchema(BaseModel):
    """User Object Schema

    A Pydantic class that defines the user schema for fetching user info.

    Attributes:
        - id (str): User's unique identifier.
        - full_name (str): User's full name.
        - bio (Optional[str]): User's bio.
        - birthday (Optional[str]): User's birthday.
        - email (EmailStr): User's email address.
        - profile_picture (Optional[str]): A relative URL to Deta Drive for the user's profile picture.
        - user_status (Optional[int]): User's status (default: 1).
        - user_role (Optional[str]): User's role (default: "regular").
        - phone_number (Optional[str]): User's phone number (default: "12314").

    """

    id: str = Field(
        ...,
        example="6386fc625c60cfd607e97b44",
        description="User's unique identifier.",
    )
    full_name: str = Field(
        ..., example="Your full name", description="User's full name."
    )
    bio: Optional[str] = Field(..., example="bio.", description="User's bio.")
    birthday: Optional[str] = Field(
        ...,
        example=str(datetime.utcnow().date()),
        description="User's birthday.",
    )
    email: EmailStr = Field(
        ..., example="user@test.com", description="User's email address."
    )
    profile_picture: Optional[str] = Field(
        ...,
        example="A relative URL to Deta Drive.",
        description="A relative URL to the user's profile picture.",
    )
    user_status: Optional[int] = Field(
        default=1, example=1, description="User's status (default: 1)."
    )
    user_role: Optional[str] = Field(
        default="regular",
        example="regular",
        description="User's role (default: 'regular').",
    )
    phone_number: Optional[str] = Field(
        default="12314",
        example="12314",
        description="User's phone number (default: '12314').",
    )


class PersonalInfo(BaseModel):
    """Personal Information

    A Pydantic class that defines the user schema for updating user info.

    Attributes:
        - full_name (str): User's full name.
        - bio (str): User's bio.
        - birthday (str): User's birthday.
        - phone_number (str): User's phone number.

    """

    full_name: str = Field(
        ..., example="Full name.", description="User's full name."
    )
    bio: str = Field(..., example="bio.", description="User's bio.")
    programming_language: str = Field(
        ..., example="python", description="User's programming language."
    )


class LogoutSchema(BaseModel):
    """Personal Information

    A Pydantic class that defines the user schema for logging out a user.
    """

    token: str = Field(..., example="123456789", description="User's token.")
