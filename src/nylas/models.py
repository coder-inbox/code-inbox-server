"""🔑 Nylas Model Module

This module defines the data model for Nylas access tokens.

Classes:
    AccessToken: Represents an access token with user association.
"""

from bson import (
    ObjectId,
)
from datetime import (
    datetime,
)
from odmantic import (
    Field,
    Model,
)
from typing import (
    List,
    Optional,
)


class AccessToken(Model):
    """The AccessToken model represents user access tokens.

    Args:
        Model (odmantic.Model): The base Odmantic model.

    Attributes:
        user (ObjectId): The user id associated with the access token.
        tokens (List[str]): A list of access tokens.
        creation_date (Optional[datetime]): The creation date of the access token
            (default is the current UTC time).
        modified_date (Optional[datetime]): The last modification date of the access token
            (default is the current UTC time).
    """

    user: ObjectId
    tokens: List[str] = []
    creation_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    modified_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
