"""👤 User Models Module 📦

This module defines the user-related models used in the application.

Classes:
    - UserStatus (enum): Enumeration of user statuses (ACTIVE or DISABLED).
    - UserRole (enum): Enumeration of user roles (REGULAR or ADMIN).
    - User (odmantic.Model): Represents a user with various attributes.

Attributes:
    - __all__ (list): List of symbols exported by this module.

Dependencies:
    - datetime: For handling date and time.
    - enum: For defining enumerations.
    - odmantic: For defining data models.
    - pydantic.EmailStr: For validating email addresses.
    - typing.Optional: For indicating optional fields.

"""

from datetime import (
    datetime,
)
from enum import Enum
from odmantic import (
    Field,
    Model,
)
from pydantic import (
    EmailStr,
)
from typing import (
    Optional,
)


class UserStatus(int, Enum):
    """🟢 UserStatus Enumeration

    This enumeration defines the possible statuses for a user.

    Members:
        - ACTIVE (int): Represents an active user (1).
        - DISABLED (int): Represents a disabled user (0).

    """

    ACTIVE = 1
    DISABLED = 0


class UserRole(str, Enum):
    """🔑 UserRole Enumeration

    This enumeration defines the possible roles for a user.

    Members:
        - REGULAR (str): Represents a regular user.
        - ADMIN (str): Represents an admin user.

    """

    REGULAR = "regular"
    ADMIN = "admin"


class User(Model):
    """👤 User Model

    This model represents a user with various attributes.

    Fields:
        - full_name (Optional[str]): Full name of the user.
        - birthday (Optional[str]): User's birthday.
        - bio (Optional[str]): User's bio.
        - email (EmailStr): User's email address.
        - profile_picture (Optional[str]): URL to the user's profile picture.
        - phone_number (Optional[str]): User's phone number.
        - programming_language (Optional[str]): User's programming language.
        - calendar (Optional[str]): User's calendar ID.
        - user_status (Optional[UserStatus]): User's status (default: ACTIVE).
        - user_role (Optional[UserRole]): User's role (default: REGULAR).
        - creation_date (Optional[datetime]): User's creation date (auto-generated).
        - modified_date (Optional[datetime]): User's last modification date (auto-generated).

    """

    full_name: Optional[str] = Field(
        index=True, description="Full name of the user."
    )
    birthday: Optional[str] = Field(default="", description="User's birthday.")
    bio: Optional[str] = Field(default="", description="User's bio.")
    email: EmailStr = Field(index=True, description="User's email address.")
    profile_picture: Optional[str] = Field(
        default="", description="URL to the user's profile picture."
    )
    phone_number: Optional[str] = Field(
        default="", description="User's phone number."
    )
    programming_language: Optional[str] = Field(
        default="", description="User's programming language."
    )
    calendar: Optional[str] = Field(
        default="", description="User's calendar ID."
    )
    user_status: Optional[UserStatus] = Field(
        default=UserStatus.ACTIVE.value, description="User's status."
    )
    user_role: Optional[UserRole] = Field(
        default=UserRole.REGULAR.value, description="User's role."
    )
    creation_date: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="User's creation date."
    )
    modified_date: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="User's last modification date.",
    )


__all__ = [
    "UserStatus",
    "UserRole",
    "User",
]
