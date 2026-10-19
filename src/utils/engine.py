"""🔧 Utils Engine Module 🚀

This module contains functions for initializing database connections and other utility tasks.

Functions:
    - init_engine_app(app: FastAPI) -> None: Creates database connections and initializes application state.

Dependencies:
    - FastAPI: For creating web applications.
    - motor.motor_asyncio.AsyncIOMotorClient: For asynchronous MongoDB connections.
    - odmantic.AIOEngine: For asynchronous database engine.
    - src.config.settings: Application configuration settings.
    - nylas.APIClient: For Nylas API client.

"""

from fastapi import (
    FastAPI,
)
from motor.motor_asyncio import (
    AsyncIOMotorClient,
)
from odmantic import (
    AIOEngine,
)

from nylas import (
    APIClient,
)
from src.config import (
    settings,
)
from src.utils import (
    openai_api,
)


async def init_engine_app(app: FastAPI) -> None:
    """Initialize Engine App

    Creates database and connections to the database.

    This function creates a MongoDB client instance,
    and an Odmantic engine and stores them in the
    application's state property.

    Args:
        app (FastAPI): FastAPI application instance.

    """
    app_settings = settings()

    client = AsyncIOMotorClient(
        app_settings.db_url, maxPoolSize=30, minPoolSize=30
    )
    database = client.get_default_database()
    assert database.name == app_settings.MONGODB_DATABASE
    engine = AIOEngine(client=client, database=app_settings.MONGODB_DATABASE)
    app.state.client = client
    app.state.engine = engine
    app.state.nylas = APIClient(
        app_settings.NYLAS_CLIENT_ID,
        app_settings.NYLAS_CLIENT_SECRET,
        app_settings.NYLAS_API_SERVER,
    )
    app.state.nylas.update_application_details(
        redirect_uris=[app_settings.CLIENT_URI]
    )
    app.state.openai = openai_api.OpenAIAPI(
        api_token=app_settings.OPENAI_API_KEY
    )
