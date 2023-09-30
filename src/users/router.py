"""🌐 Users Router Module 📡

This module defines the API routes related to user management in the application.

Classes and Functions:
    - router (APIRouter): FastAPI router for user-related routes.
    - logout (async function): Log out a user by removing their access token.
    - upload_profile_image (async function): Upload a user's profile image to Deta Drive.
    - get_profile_user_image (async function): Get a user's profile image from Deta Drive.
    - update_personal_information (async function): Update a user's personal information.

Dependencies:
    - Deta: For working with Deta Drive.
    - fastapi: For creating API routes.
    - odmantic.session: For database sessions.
    - typing: For type hints and annotations.

External Dependencies:
    - src.config: Application configuration settings.
    - src.users.crud: User CRUD operations.
    - src.users.schemas: User-related Pydantic schemas.
    - src.utils.dependencies: Custom FastAPI dependencies.

"""

from apscheduler.schedulers.background import (
    BackgroundScheduler,
)
from asyncio import (
    ensure_future,
)
from deta import Deta
from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    responses,
)
from odmantic.session import (
    AIOSession,
)
from typing import (
    Any,
    Dict,
    Union,
)

from src.config import (
    settings,
)
from src.nylas import (
    crud as nylas_crud,
)
from src.users import (
    crud as users_crud,
    schemas as users_schemas,
)
from src.utils import (
    dependencies,
)

router = APIRouter(prefix="/api/v1")

# initialize with a project key
deta = Deta(settings().DETA_PROJECT_KEY)

# create and use as many Drives as you want!
profile_images = deta.Drive("profile-images")


@router.post(
    "/user/logout",
    response_model=Dict[str, str],
    status_code=200,
    name="user:logout",
)
async def logout(
    token: users_schemas.LogoutSchema,
    current_user: users_schemas.UserObjectSchema = Depends(
        dependencies.get_current_user
    ),
    session: AIOSession = Depends(dependencies.get_db_transactional_session),
) -> Dict[str, Any]:
    """
    Log out a user from the app by removing the access token from the list.
    """
    try:
        await users_crud.remove_token(current_user.id, token, session)
        return {"status": 200, "message": "Good Bye!"}
    except Exception:
        return {"status_code": 400, "message": "Something went wrong!"}


@router.put(
    "/user/profile-image",
    response_model=None,
    status_code=200,
    name="user:profile-image",
)
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: users_schemas.UserObjectSchema = Depends(
        dependencies.get_current_user
    ),
    session: AIOSession = Depends(dependencies.get_db_transactional_session),
) -> Dict[str, Any]:
    """
    Upload an image to a Deta drive and associate it with the user's profile.
    """
    try:
        file_name = "user/" + str(current_user.id) + "/" + "profile.png"
        profile_images.put(file_name, file.file)
        await users_crud.update_profile_picture(
            email=current_user.email, file_name=file_name, session=session
        )
        return {
            "status_code": 200,
            "image": file_name,
        }

    except Exception as e:
        print(e)
        return {"status_code": 400, "message": "Something went wrong!"}


@router.get(
    "/user/{user_id}/profile.png",
    response_model=None,
    status_code=200,
    name="user:profile-user-image",
)
async def get_profile_user_image(
    user_id: str,
) -> Union[responses.StreamingResponse, Dict[str, Any]]:
    """
    Update a user's personal information.
    """
    try:
        img = profile_images.get(f"user/{user_id}/profile.png")
        return responses.StreamingResponse(
            img.iter_chunks(), media_type="image/png"
        )
    except Exception:
        return {"status_code": 400, "message": "Something went wrong!"}


@router.put(
    "/user/profile",
    response_model=Dict[str, str],
    status_code=200,
    name="user:profile-image",
)
async def update_personal_information(
    personal_info: users_schemas.PersonalInfo,
    current_user: users_schemas.UserObjectSchema = Depends(
        dependencies.get_current_user
    ),
    session: AIOSession = Depends(dependencies.get_db_transactional_session),
) -> Dict[str, Any]:
    """
    An endpoint for updating users personel info.
    """
    try:
        await users_crud.update_user_info(personal_info, current_user, session)
        return {
            "status_code": 200,
            "message": "Your personal information has been updated successfully!",
        }
    except Exception:
        return {"status_code": 400, "message": "Something went wrong!"}


@router.put(
    "/user/language",
    response_model=Dict[str, Any],
    status_code=200,
    name="user:language",
)
async def update_language(
    request_body: users_schemas.LanguageSchema,
    current_user: users_schemas.UserObjectSchema = Depends(
        dependencies.get_current_user
    ),
    session: AIOSession = Depends(dependencies.get_db_transactional_session),
) -> Dict[str, Any]:
    """
    Set the programming language for a specific user using their access token.
    """
    try:
        from src.main import (
            code_app,
        )

        scheduler = BackgroundScheduler()
        user_info = users_schemas.PersonalInfo(
            full_name=current_user.full_name,
            bio=current_user.bio,
            programming_language=request_body.language,
        )
        await users_crud.update_user_info(user_info, current_user, session)
        # send a welcome email in the background
        ensure_future(nylas_crud.send_welcome_email(current_user.email))
        # send an algorithm email in the background
        ensure_future(
            code_app.state.openai.async_send_algorithm_email(
                current_user.email, request_body.language
            )
        )
        # send an algorithm email every 24 hours
        scheduler.add_job(
            code_app.state.openai.send_algorithm_email,
            "interval",
            hours=24,
            args=(current_user.email, request_body.language),
        )
        scheduler.start()
        return {
            "status_code": 200,
            "message": "Your programming language has been updated successfully!",
        }
    except Exception as e:
        print(e)
        return {"status_code": 400, "message": "Something went wrong!"}
