from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.database.mongo import (
    client,
    close_mongodb,
)

from app.modules.poi.presentation.controllers.poi_controller import router as poi_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    client.admin.command("ping")
    print("MongoDB connected successfully")

    yield

    close_mongodb()


app = FastAPI(lifespan=lifespan)
app.include_router(poi_router, prefix="/api")