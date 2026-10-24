from fastapi import FastAPI

from app.presentation.routers.poi_router import router as poi_router

app = FastAPI(title="POI Services API")

app.include_router(poi_router)


@app.get("/")
def health_check():
    return {"status": "ok"}