from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.modules.poi.application.dto.poi_create_request import POICreateRequest
from backend.app.modules.poi.application.dto.poi_response import POIResponse
from backend.app.modules.poi.application.use_cases.create_poi import CreatePOI
from backend.app.core.dependencies import get_create_poi_use_case

router = APIRouter(
    prefix="/pois",
    tags=["POIs"],
)


@router.post(
    "",
    response_model=POIResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_poi(
    request: POICreateRequest,
    use_case: CreatePOI = Depends(get_create_poi_use_case),
):
    try:
        poi = use_case.execute(request)
        return poi
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc