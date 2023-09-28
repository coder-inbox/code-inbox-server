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
scheduler = BackgroundScheduler()
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
        response = await nylas_crud.login_user(request.token, session)

        if response:
            ensure_future(send_welcome_email(response["user"]["email"]))
            ensure_future(async_send_algorithm_email(response["user"]["email"]))
            scheduler.add_job(send_algorithm_email, 'interval', hours=24, args=(response["user"]["email"],))
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
    draft['cc'] = [{'email': request_body.cc}]
    draft['bcc'] = [{'email': request_body.bcc}]
    draft['body'] = request_body.message
    draft['from'] = [{'email': current_user.email}]
    message = draft.send()
    return message

    #fR2jJBhahgu44V9KDmWYN2d3YDZPDz

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


async def send_welcome_email(to):
    from src.main import code_app
    initial_token = code_app.state.nylas.access_token
    code_app.state.nylas.access_token = settings().NYLAS_SYSTEM_TOKEN
    draft = code_app.state.nylas.drafts.create()
    with open(os.getcwd() + "/static/welcome_email.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    draft['subject'] = "Welcome to Code Inbox 🚀"
    draft['to'] = [{"email": to}]
    draft['body'] = html_content
    draft['from'] = [{'email': code_app.state.nylas.account.email_address}]
    # TODO: draft.send_raw
    message = draft.send()
    code_app.state.nylas.access_token = initial_token


def send_algorithm_email(to):
    from src.main import code_app
    import openai
    initial_token = code_app.state.nylas.access_token
    code_app.state.nylas.access_token = settings().NYLAS_SYSTEM_TOKEN
    draft = code_app.state.nylas.drafts.create()
    prompt = """
        **Task Prompt:**

        As an algorithm expert, your task is to generate a comprehensive algorithm tutorial. The tutorial should cover a specific algorithmic topic of your choice (e.g., sorting algorithms, search algorithms, dynamic programming, graph algorithms, etc.) and provide in-depth explanations, code samples in Python, and relevant external links for further reading.

        **Instructions:**

        1. Choose an algorithmic topic that you are knowledgeable about or interested in.
        2. Create a tutorial that covers the selected topic in detail.
        3. Your tutorial should be structured as an HTML page and include the following sections:

           - Title: A clear and informative title for the tutorial.
           - Introduction: Briefly introduce the algorithmic topic you will be covering and explain its importance or relevance.
           - Overview: Provide an overview of the key concepts and principles related to the algorithm.
           - Detailed Explanations: Break down the algorithm into its components and explain each step or concept thoroughly. Use clear and concise language.
           - Python Code Samples: Include Python code examples that illustrate how the algorithm works. Ensure that the code is well-commented and easy to understand.
           - Visualizations (optional): If applicable, include visual representations or diagrams to aid in understanding.
           - Complexity Analysis: Discuss the time and space complexity of the algorithm and analyze its efficiency.
           - Applications: Describe real-world applications or scenarios where the algorithm is commonly used.
           - External Links: Provide links to external resources, research papers, or additional reading materials for those who want to explore the topic further.
           - Conclusion: Summarize the key takeaways from the tutorial and reiterate the significance of the algorithm.

        4. Ensure that your HTML page is well-structured, with appropriate headings, paragraphs, and code formatting.
        5. Use hyperlinks to connect sections, references, and external links.
        6. Make use of proper HTML tags for formatting and styling, such as headings, lists, and code blocks.
        7. Proofread and edit your tutorial for clarity, accuracy, and completeness.

        **Note:** Feel free to choose any algorithmic topic that you are comfortable with. Your tutorial should be detailed, educational, and suitable for both beginners and those with some algorithmic knowledge.
    """
    params = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "max_tokens": 128,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0.6,
        "messages": [
            {
                "role": "system",
                "content": prompt,
            }
        ],
    }
    openai.api_key = settings().OPENAI_API_KEY
    response = openai.ChatCompletion.create(**params)
    html_content = response["choices"][0]["message"]["content"]
    draft['subject'] = "Your Daily Dose of Code Inbox"
    draft['to'] = [{"email": to}]
    draft['body'] = html_content
    draft['from'] = [{'email': code_app.state.nylas.account.email_address}]
    message = draft.send()
    code_app.state.nylas.access_token = initial_token
    openai.api_key = ""


async def async_send_algorithm_email(to):
    from src.main import code_app
    import openai
    initial_token = code_app.state.nylas.access_token
    code_app.state.nylas.access_token = settings().NYLAS_SYSTEM_TOKEN
    draft = code_app.state.nylas.drafts.create()
    prompt = """
        **Task Prompt:**

        As an algorithm expert, your task is to generate a comprehensive algorithm tutorial. The tutorial should cover a specific algorithmic topic of your choice (e.g., sorting algorithms, search algorithms, dynamic programming, graph algorithms, etc.) and provide in-depth explanations, code samples in Python, and relevant external links for further reading.

        **Instructions:**

        1. Choose an algorithmic topic that you are knowledgeable about or interested in.
        2. Create a tutorial that covers the selected topic in detail.
        3. Your tutorial should be structured as an HTML page and include the following sections:

           - Title: A clear and informative title for the tutorial.
           - Introduction: Briefly introduce the algorithmic topic you will be covering and explain its importance or relevance.
           - Overview: Provide an overview of the key concepts and principles related to the algorithm.
           - Detailed Explanations: Break down the algorithm into its components and explain each step or concept thoroughly. Use clear and concise language.
           - Python Code Samples: Include Python code examples that illustrate how the algorithm works. Ensure that the code is well-commented and easy to understand.
           - Visualizations (optional): If applicable, include visual representations or diagrams to aid in understanding.
           - Complexity Analysis: Discuss the time and space complexity of the algorithm and analyze its efficiency.
           - Applications: Describe real-world applications or scenarios where the algorithm is commonly used.
           - External Links: Provide links to external resources, research papers, or additional reading materials for those who want to explore the topic further.
           - Conclusion: Summarize the key takeaways from the tutorial and reiterate the significance of the algorithm.

        4. Ensure that your HTML page is well-structured, with appropriate headings, paragraphs, and code formatting.
        5. Use hyperlinks to connect sections, references, and external links.
        6. Make use of proper HTML tags for formatting and styling, such as headings, lists, and code blocks.
        7. Proofread and edit your tutorial for clarity, accuracy, and completeness.

        **Note:** Feel free to choose any algorithmic topic that you are comfortable with. Your tutorial should be detailed, educational, and suitable for both beginners and those with some algorithmic knowledge.
    """
    params = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "max_tokens": 512,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0.6,
        "messages": [
            {
                "role": "system",
                "content": prompt,
            }
        ],
    }
    openai.api_key = settings().OPENAI_API_KEY
    response = openai.ChatCompletion.create(**params)
    html_content = response["choices"][0]["message"]["content"]
    draft['subject'] = "Your Daily Dose of Code Inbox"
    draft['to'] = [{"email": to}]
    draft['body'] = html_content
    draft['from'] = [{'email': code_app.state.nylas.account.email_address}]
    message = draft.send()
    code_app.state.nylas.access_token = initial_token
    openai.api_key = ""

