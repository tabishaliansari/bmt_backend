"""BMT FastAPI app: the API under /api/v1 and the static frontend at /."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from app.ai.errors import AIError, AITimeout
from app.config import get_settings
from app.db import get_db
from app.routers import briefs, editors, health, orders, uploads
from app.seed import seed

API_PREFIX = "/api/v1"

logging.basicConfig(level=logging.INFO, format="%(levelname)s:  %(name)s: %(message)s")


def error_response(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


def create_app() -> FastAPI:
    settings = get_settings()
    seed(get_db())
    app = FastAPI(title="BMT API", version="0.1.0")

    @app.exception_handler(HTTPException)
    async def http_error(_: Request, exc: HTTPException) -> JSONResponse:
        return error_response(exc.status_code, f"http_{exc.status_code}", str(exc.detail))

    @app.exception_handler(AIError)
    async def ai_error(_: Request, exc: AIError) -> JSONResponse:
        if isinstance(exc, AITimeout):
            return error_response(504, "ai_timeout", str(exc))
        return error_response(502, "ai_error", str(exc))

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(422, "invalid_request", str(exc.errors()))

    for router in (health.router, editors.router, uploads.router, briefs.router, orders.router):
        app.include_router(router, prefix=API_PREFIX)

    if settings.frontend_dir.is_dir():
        app.mount("/", StaticFiles(directory=settings.frontend_dir, html=True), name="frontend")

    return app


app = create_app()
