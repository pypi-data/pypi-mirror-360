from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from doc81.core.config import Config
from doc81.rest.routes import health, users, templates, companies


def create_app() -> FastAPI:
    config = Config()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        from doc81.core.database import init_db

        init_db()
        yield

    app = FastAPI(
        title="Doc81 REST API", version="0.1.0", config=config, lifespan=lifespan
    )

    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(templates.router)
    app.include_router(companies.router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()


def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
