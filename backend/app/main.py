from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.database.mongo import (
    client,
    close_mongodb,
)
from app.modules.menu.presentation.controllers.menu_item_controller import (
    router as menu_item_router,
)
from app.modules.poi.presentation.controllers.poi_controller import router as poi_router
from app.modules.role.presentation.controllers.role_controller import (
    router as role_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    client.admin.command("ping")
    print("MongoDB connected successfully")

    yield

    close_mongodb()


app = FastAPI(lifespan=lifespan)
app.include_router(poi_router, prefix="/api")
app.include_router(menu_item_router, prefix="/api")
app.include_router(role_router, prefix="/api")
