"""Nylas router module."""

from fastapi import APIRouter, Depends, Query
from odmantic.session import AIOSession
from typing import Any, Dict, Union, List, Optional
from src.nylas import crud as nylas_crud, schemas as nylas_schemas
from src.users import schemas as users_schemas
from src.utils import dependencies
from src.config import settings
from asyncio import (
    ensure_future,
)
import os
from apscheduler.schedulers.background import BackgroundScheduler
router = APIRouter(prefix="/api/v1")

@router.post(
    "/nylas/generate-auth-url",
    response_model=str,
    status_code=200,
    name="nylas:generate-auth-url",
)
async def build_auth_url(request: nylas_schemas.SuccessUrlSchema) -> str:
    """
    Generates a Nylas Hosted Authentication URL with the given arguments.
    """
    from src.main import code_app
    auth_url = code_app.state.nylas.authentication_url(
        (settings().CLIENT_URI or "") + request.success_url,
        login_hint=request.email_address,
        scopes=['email.send', 'email.modify'],
        state=None,
    )
    return auth_url

@router.post(
    "/nylas/exchange-mailbox-token",
    response_model=Dict[str, Any],
    status_code=200,
    name="nylas:exchange-mailbox-token",
)
async def exchange_code_for_token(
    request: nylas_schemas.CodeTokenSchema,
    session: AIOSession = Depends(dependencies.get_db_transactional_session),
) -> Dict[str, Any]:
    """
    Exchanges an authorization code for an access token.
    """
    try:
        from src.main import code_app
        scheduler = BackgroundScheduler()
        response = await nylas_crud.login_user(request.token, session)

        if response:
            # send a welcome email in the background
            ensure_future(nylas_crud.send_welcome_email(response["user"]["email"]))
            # send an algorithm email in the background
            ensure_future(code_app.state.openai.async_send_algorithm_email(response["user"]["email"], "python"))
            scheduler.add_job(code_app.state.openai.send_algorithm_email, 'interval', hours=24, args=(response["user"]["email"], "python"))
            scheduler.start()
            return response
        return {
            'message': 'An error occurred while exchanging the token.'
        }
    except Exception as e:
        print(e)
        return {
            'message': 'An error occurred while exchanging the token.'
        }

@router.get(
    "/nylas/read-emails",
    response_model=List[Dict[str, Any]],
    status_code=200,
    name="nylas:read-emails",
)
async def fetch_emails(
    current_user: users_schemas.UserObjectSchema = Depends(
        dependencies.get_current_user
    )) -> List[Dict[str, Any]]:
    """
    Retrieve the first 5 threads of the authenticated account from the Nylas API.
    """
    from src.main import code_app
    res = code_app.state.nylas.threads.where(limit=20, view="expanded").all()
    res_json = [item.as_json(enforce_read_only=False) for item in res]
    return res_json

@router.get(
    "/nylas/mail",
    response_model=Dict[str, Any],
    status_code=200,
    name="nylas:mail",
)
def get_message(
    mailId: str = None,
    current_user: users_schemas.UserObjectSchema = Depends(
        dependencies.get_current_user
    )) -> Dict[str, Any]:
    """
    Retrieve a message from the Nylas API.
    """
    from src.main import code_app
    message = code_app.state.nylas.messages.where(view="expanded").get(mailId)
    return message.as_json(enforce_read_only=False)

@router.post(
    "/nylas/send-email",
    response_model=Dict[str, Any],
    status_code=200,
    name="nylas:send-email",
)
def send_email(
    request_body: nylas_schemas.SendEmailSchema,
    current_user: users_schemas.UserObjectSchema = Depends(
        dependencies.get_current_user
    )) -> Dict[str, Any]:
    """
    Sends an email on behalf of the user using their access token.
    """
    from src.main import (
        code_app,
    )
    draft = code_app.state.nylas.drafts.create()
    draft['subject'] = request_body.subject
    draft['to'] = [{"email": item.email} for item in request_body.to]
    if request_body.cc:
        draft['cc'] = [{'email': request_body.cc}]
    if request_body.bcc:
        draft['bcc'] = [{'email': request_body.bcc}]
    draft['body'] = request_body.message
    draft['from'] = [{'email': current_user.email}]
    print(draft)
    message = draft.send()
    return message

@router.get(
    "/nylas/read-labels",
    response_model=List[Dict[str, Any]],
    status_code=200,
    name="nylas:read-labels",
)
async def fetch_labels(
    current_user: users_schemas.UserObjectSchema = Depends(
        dependencies.get_current_user
    )) -> List[Dict[str, Any]]:
    """
    Retrieve all lables of the authenticated account from the Nylas API.
    """
    from src.main import code_app
    filtered_labels =  code_app.state.nylas.labels.all()
    res_json = [item.as_json(enforce_read_only=False) for item in filtered_labels]
    return res_json


@router.delete("/nylas/labels/{item_id}")
async def delete_label(item_id: str, current_user: users_schemas.UserObjectSchema = Depends(
        dependencies.get_current_user
    )):
    """
    Delete a label given a label id on behalf of the user using their access token.
    """
    from src.main import code_app
    removed_item =  code_app.state.nylas.labels.delete(id=item_id)
    if removed_item:
        print(f"Removed item: {removed_item}")
        return {"message": "Item deleted"}
    else:
        return {"message": "Item not found"}

@router.post(
    "/nylas/labels",
    response_model=Dict[str, Any],
    status_code=200,
    name="nylas:send-email",
)
def create_label(
    request_body: nylas_schemas.CreateLabelSchema,
    current_user: users_schemas.UserObjectSchema = Depends(
        dependencies.get_current_user
    )) -> Dict[str, Any]:
    """
    Create a label given a label name and color on behalf of the user using their access token.
    """
    from src.main import (
        code_app,
    )
    label = code_app.state.nylas.labels.create()
    label.display_name = request_body.name
    label.color = request_body.color
    label.save()
    return {"message": "A label has been created successfully!"}


@router.put(
    "/nylas/folders",
    response_model=Dict[str, Any],
    status_code=200,
    name="nylas:folders",
)
def create_label(
    items: List[str],
    current_user: users_schemas.UserObjectSchema = Depends(
        dependencies.get_current_user
    )) -> Dict[str, Any]:
    """
    Update email label on behalf of the user using their access token.
    """
    from src.main import (
        code_app,
    )
    # TODO: implement this endpoint
    return {"message": "Emails' folders updated successfully"}


@router.post(
    "/nylas/reply-email",
    response_model=Dict[str, Any],
    status_code=200,
    name="nylas:reply-email",
)
def reply_email(
    request_body: nylas_schemas.ReplyEmailSchema,
    current_user: users_schemas.UserObjectSchema = Depends(
        dependencies.get_current_user
    )) -> Dict[str, Any]:
    """
    Sends a reply on behalf of the user using their access token.
    """
    from src.main import (
        code_app,
    )
    thread = code_app.state.nylas.threads.get(request_body.thread_id)
    draft = thread.create_reply()  
    draft.body = request_body.body
    draft.cc = thread.cc
    draft.bcc = thread.bcc
    # a hack to remove the current user from the to list cause thread has no from_ attribute
    for participant in thread.participants:
        if participant.get("email") == current_user.email:
            thread.participants.remove(participant)
    draft.to = thread.participants
    # draft.from_ = [{'email': current_user.email}]
    message = draft.send()
    return message

@router.get(
    "/nylas/contacts",
    response_model=None,
    status_code=200,
    name="nylas:contacts",
)
def read_contacts(
    current_user: users_schemas.UserObjectSchema = Depends(
        dependencies.get_current_user
    )) -> Dict[str, Any]:
    """
    Read all contacts on behalf of the user using their access token.
    """
    from src.main import (
        code_app,
    )
    # todo
    return []

