from typing import Annotated

from app.core.dependencies import get_menu_item_service
from app.modules.menu.application.dto.menu_item_create_request import (
    MenuItemCreateRequest,
)
from app.modules.menu.application.dto.menu_item_response import MenuItemResponse
from app.modules.menu.application.services.menu_item_service import MenuItemService
from app.modules.menu.domain.entities.menu_item import MenuItem
from app.modules.menu.infrastructure.exceptions.menu_item_exceptions import (
    MenuItemNotFound,
)
from fastapi import APIRouter, Depends, HTTPException, Response, status

router = APIRouter(prefix="/menu-items", tags=["Menu items"])


def to_response(menu_item: MenuItem) -> MenuItemResponse:
    return MenuItemResponse(
        id=menu_item.id,
        poi_id=menu_item.poi_id,
        name=menu_item.name,
        price=menu_item.price,
    )


@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    request: MenuItemCreateRequest,
    service: Annotated[MenuItemService, Depends(get_menu_item_service)],
):
    try:
        return to_response(service.create(request))
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/poi/{poi_id}", response_model=list[MenuItemResponse])
def get_menu_items_by_poi_id(
    poi_id: str,
    service: Annotated[MenuItemService, Depends(get_menu_item_service)],
):
    return [to_response(item) for item in service.get_by_poi_id(poi_id)]


@router.get("/{menu_item_id}", response_model=MenuItemResponse)
def get_menu_item(
    menu_item_id: str,
    service: Annotated[MenuItemService, Depends(get_menu_item_service)],
):
    menu_item = service.get_by_id(menu_item_id)
    if menu_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )
    return to_response(menu_item)


@router.put("/{menu_item_id}", response_model=MenuItemResponse)
def update_menu_item(
    menu_item_id: str,
    request: MenuItemCreateRequest,
    service: Annotated[MenuItemService, Depends(get_menu_item_service)],
):
    try:
        return to_response(service.update(menu_item_id, request))
    except MenuItemNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete("/{menu_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    menu_item_id: str,
    service: Annotated[MenuItemService, Depends(get_menu_item_service)],
):
    if not service.delete(menu_item_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
