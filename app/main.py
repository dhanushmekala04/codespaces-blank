from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import appointments, billing, chat, patients, timeline
from app.db.mongo import close_mongo, init_mongo
from app.db.redis import close_redis, init_redis
from config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_mongo()
    await init_redis()
    yield
    await close_mongo()
    await close_redis()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Patient care workflow platform",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat.router)
    app.include_router(patients.router)
    app.include_router(appointments.router)
    app.include_router(billing.router)
    app.include_router(timeline.router)

    return app


app = create_app()
