from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.database.mongo import (
    client,
    close_mongodb,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    client.admin.command("ping")
    print("MongoDB connected successfully")

    yield

    close_mongodb()


app = FastAPI(lifespan=lifespan)