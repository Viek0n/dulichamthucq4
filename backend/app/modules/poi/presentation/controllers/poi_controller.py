from typing import Annotated

from app.core.dependencies import get_poi_service
from app.modules.poi.application.services.poi_service import POIService
from app.modules.poi.domain.entities.poi import POI
from app.modules.poi.presentation.schemas.poi_create_request import POICreateRequest
from app.modules.poi.presentation.schemas.poi_response import POIResponse
from fastapi import APIRouter, Depends, HTTPException, Response, status

router = APIRouter(prefix="/pois", tags=["POI"])


def to_response(poi: POI) -> POIResponse:
    return POIResponse(
        id=poi.id,
        slug=poi.slug,
        name=poi.name,
        address=poi.address,
        open_at=str(poi.open_at.time),
        close_at=str(poi.close_at.time),
        contact=poi.contact,
        description=poi.description,
        image=poi.image,
        latitude=poi.position.latitude,
        longitude=poi.position.longitude,
        trigger_radius=poi.trigger_radius,
        is_delete=poi.is_delete,
        poi_owner_id=poi.poi_owner_id,
    )


@router.post("", response_model=POIResponse, status_code=status.HTTP_201_CREATED)
def create_poi(
    request: POICreateRequest,
    service: Annotated[POIService, Depends(get_poi_service)],
):
    try:
        # Temporary example; normally obtain this from JWT authentication.
        poi = service.create(request, owner_id="6af297303d6708359f1a68d7")

        return to_response(poi)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.delete("/{poi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poi(
    poi_id: str,
    service: Annotated[POIService, Depends(get_poi_service)],
):
    if not service.delete(poi_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POI not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
