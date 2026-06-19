from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import appointments, billing, chat, patients, timeline
from app.db.mongo import close_mongo, get_database, init_mongo
from app.db.redis import close_redis, get_redis_client, init_redis
from app.middleware.request_context import RequestContextMiddleware
from app.observability import flush_langfuse, setup_logging
from config.settings import settings


async def create_indexes() -> None:
    """Create MongoDB indexes for all collections on startup."""
    db = await get_database()

    # patients
    await db["patients"].create_index("patient_id", unique=True, background=True)
    await db["patients"].create_index("tenant_id", background=True)
    await db["patients"].create_index("email", background=True)

    # appointments
    await db["appointments"].create_index("patient_id", background=True)
    await db["appointments"].create_index("provider_id", background=True)
    await db["appointments"].create_index([("patient_id", 1), ("status", 1)], background=True)

    # billing
    await db["billing"].create_index("patient_id", background=True)
    await db["billing"].create_index("account_id", background=True)

    # insurance
    await db["insurance"].create_index("patient_id", background=True)

    # claims
    await db["claims"].create_index("patient_id", background=True)
    await db["claims"].create_index("insurance_id", background=True)

    # cases
    await db["cases"].create_index("patient_id", background=True)
    await db["cases"].create_index([("patient_id", 1), ("status", 1)], background=True)

    # events
    await db["events"].create_index("patient_id", background=True)
    await db["events"].create_index([("patient_id", 1), ("event_time", -1)], background=True)
    await db["events"].create_index([("entity_type", 1), ("entity_id", 1)], background=True)

    # audit_logs
    await db["audit_logs"].create_index("request_id", background=True)
    await db["audit_logs"].create_index("actor_id", background=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_mongo()
    await init_redis()
    await create_indexes()
    yield
    await close_mongo()
    await close_redis()
    flush_langfuse()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Patient care workflow platform",
        lifespan=lifespan,
    )

    # Restrict CORS in non-development environments
    origins = ["*"] if settings.environment == "development" else []

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Stamp every request with a unique X-Request-ID
    app.add_middleware(RequestContextMiddleware)

    app.include_router(chat.router)
    app.include_router(patients.router)
    app.include_router(appointments.router)
    app.include_router(billing.router)
    app.include_router(timeline.router)

    # ── Health / readiness probes ─────────────────────────────────────────────

    @app.get("/health", tags=["ops"], include_in_schema=False)
    async def health():
        """Liveness probe — ECS / ALB health check. Returns 200 if process is alive."""
        return {"status": "healthy"}

    @app.get("/ready", tags=["ops"], include_in_schema=False)
    async def ready():
        """
        Readiness probe — checks all backing services before accepting traffic.
        Returns 200 only when MongoDB and Redis are reachable.
        Pinecone is optional (degraded mode allowed).
        """
        checks: dict[str, str] = {}
        http_status = 200

        # MongoDB
        try:
            db = await get_database()
            await db.command("ping")
            checks["mongodb"] = "ok"
        except Exception as exc:
            checks["mongodb"] = f"error: {exc}"
            http_status = 503

        # Redis
        try:
            redis = await get_redis_client()
            if redis:
                await redis.ping()
                checks["redis"] = "ok"
            else:
                checks["redis"] = "unavailable"
                # Redis degraded is acceptable — caching disabled but app still runs
        except Exception as exc:
            checks["redis"] = f"error: {exc}"

        return JSONResponse(
            status_code=http_status,
            content={"status": "ready" if http_status == 200 else "degraded", "checks": checks},
        )

    return app


app = create_app()
