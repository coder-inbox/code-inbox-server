"""🔗 Utils Dependencies Module 🧩

This module contains utility functions for handling dependencies and request sessions.

Functions:
    - get_db_transactional_session(request: Request) -> AsyncGenerator[AIOSession, None]:
        Create and get a transactional database session.
    - get_current_user(authorization: str = Header(None), email: str = Header(None))
        -> Optional[Dict[str, Any]]: Get the current user based on authorization headers.
    - get_db_autocommit_session() -> AsyncGenerator[AIOSession, None]:
        Create and get an autocommit database session.

Dependencies:
    - odmantic.session.AIOSession: For asynchronous database sessions.
    - starlette.requests.Request: For handling HTTP requests.
    - typing: For type hints and annotations.
    - fastapi.Header: For accessing request headers.
    - fastapi.Depends: For handling dependencies.
    - fastapi.HTTPException: For raising HTTP exceptions.
    - fastapi.status: For HTTP status codes.

External Dependencies:
    - src.main.code_app: FastAPI application instance.
    - src.nylas.crud: Nylas CRUD operations.

"""

from fastapi import (
    Header,
    HTTPException,
    status,
)
from odmantic.session import (
    AIOSession,
)
from starlette.requests import (
    Request,
)
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    Optional,
)


async def get_db_transactional_session(
    request: Request,
) -> AsyncGenerator[AIOSession, None]:
    """Get Transactional Database Session

    Create and get an engine session for transactional operations.

    Args:
        request (Request): Current HTTP request.

    Yields:
        AIOSession: An asynchronous database session.
    """
    try:
        session: AIOSession = request.app.state.engine.session()
        await session.start()
        yield session
    finally:
        await session.end()
        request.app.state.nylas.access_token = None


async def get_current_user(
    authorization: str = Header(None), email: str = Header(None)
) -> Optional[Dict[str, Any]]:
    """Get Current User

    Get the current user based on authorization headers.

    Args:
        authorization (str): Authorization header containing the access token.
        email (str): Email header.

    Raises:
        HTTPException: If the token is invalid, expired, or not found.

    Returns:
        Optional[Dict[str, Any]]: The user object.

    """

    from src.main import (  # pylint: disable=C0415
        code_app,
    )
    from src.nylas import (  # pylint: disable=C0415
        crud as nylas_crud,
    )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized User!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not authorization:
        raise credentials_exception

    session: AIOSession = code_app.state.engine.session()
    await session.start()
    user = await nylas_crud.find_existed_token(email, authorization, session)
    if not user:
        raise credentials_exception

    # Set the access token for the Nylas API client
    code_app.state.nylas.access_token = authorization
    await session.end()
    return user


async def get_db_autocommit_session() -> AsyncGenerator[AIOSession, None]:
    """Get Autocommit Database Session

    Create and get an engine session for autocommit operations.

    Yields:
        AIOSession: An asynchronous database session.

    """

    from src.main import (  # pylint: disable=C0415
        code_app,
    )

    try:
        session: AIOSession = code_app.state.engine.session()
        await session.start()
        yield session
    finally:
        await session.end()
        code_app.state.nylas.access_token = None
