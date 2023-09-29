"""The nylas schemas module"""

from datetime import (
    datetime,
)
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)
from typing import (
    Dict,
    List,
    Optional,
)


class SuccessUrlSchema(BaseModel):
    """
    A Pydantic class that defines the user schema for generating a success url.
    """
    email_address: EmailStr = Field(..., description="Sender's email address", example="sender@example.com")
    success_url: Optional[str] = Field(
        ..., description="Success url", example="https://example.com/"
    )

class CodeTokenSchema(BaseModel):
    """
    A Pydantic class that defines the user schema for exchanging a code for a token.
    """
    token: str = Field(..., description="Sender token", example="XIHkPTgVfcirb6V7C8U8zNzc9mtdxr")

class MailRecipient(BaseModel):
    name: str = Field(..., description="Recipient's name", example="Receiver name")
    email: EmailStr = Field(..., description="Recipient's email address", example="recipient@example.com")

class SendEmailSchema(BaseModel):
    to: list[MailRecipient] = Field(..., description="List of recipient email addresses", example=[{"name": "Receiver name", "email": "recipient@example.com"}])
    cc: Optional[str] = Field(..., description="CC email address", example="cc@example.com")
    bcc: Optional[str] = Field(..., description="BCC email address", example="bcc@example.com")
    subject: str = Field(..., description="Email subject", example="Hello, World!")
    message: str = Field(..., description="Email message body", example="This is a test email message.")
    attachments: Optional[list[str]] = Field([], description="List of attachment URLs", example=["https://example.com/attachment1.pdf"])

class CreateLabelSchema(BaseModel):
    name: str = Field(..., description="Label Name", example="Label Name")
    color: str = Field(..., description="Label Color", example="#ffffff")

class ReplyEmailSchema(BaseModel):
    thread_id: str = Field(..., description="thread id", example="6gq33fhrgpts8wmb2sl98jdvo")
    body: str = Field(..., description="email body", example="Hello there!")

