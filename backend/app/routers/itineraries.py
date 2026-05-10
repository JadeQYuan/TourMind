from __future__ import annotations
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.dependencies import get_db, get_current_user
from app.core.security import User
from app.models import Itinerary
from app.schemas import (
    Itinerary as ItinerarySchema,
    ItineraryCreate,
    ItineraryUpdate,
    ItineraryListItem,
    ResponseModel,
)
from datetime import datetime
import secrets


router = APIRouter()


@router.get("", response_model=ResponseModel[List[ItineraryListItem]])
async def list_itineraries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Itinerary).where(Itinerary.created_by == current_user.id)
    )
    itineraries = result.scalars().all()
    return ResponseModel(data=itineraries)


@router.get("/{itinerary_id}", response_model=ResponseModel[ItinerarySchema])
async def get_itinerary(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Itinerary).where(
            Itinerary.id == itinerary_id,
            Itinerary.created_by == current_user.id,
        )
    )
    itinerary = result.scalar_one_or_none()
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found",
        )
    return ResponseModel(data=itinerary)


@router.post("", response_model=ResponseModel[ItinerarySchema])
async def create_itinerary(
    data: ItineraryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 转换details为可JSON序列化的字典
    details_data = None
    if data.details:
        details_data = []
        for day in data.details:
            day_dict = day.model_dump()
            if day_dict.get("date"):
                day_dict["date"] = day_dict["date"].isoformat()
            if day_dict.get("attachments"):
                for att in day_dict["attachments"]:
                    if att.get("created_at"):
                        att["created_at"] = att["created_at"].isoformat()
            details_data.append(day_dict)

    itinerary = Itinerary(
        **data.model_dump(exclude={"details"}),
        created_by=current_user.id,
        status="not_started",
        details=details_data,
    )
    db.add(itinerary)
    await db.commit()
    await db.refresh(itinerary)
    return ResponseModel(data=itinerary)


@router.put("/{itinerary_id}", response_model=ResponseModel[ItinerarySchema])
async def update_itinerary(
    itinerary_id: int,
    data: ItineraryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Itinerary).where(
            Itinerary.id == itinerary_id,
            Itinerary.created_by == current_user.id,
        )
    )
    itinerary = result.scalar_one_or_none()
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found",
        )

    # 更新基本字段
    update_data = data.model_dump(exclude_unset=True, exclude={"details"})
    for field, value in update_data.items():
        setattr(itinerary, field, value)

    # 更新details
    if data.details is not None:
        details_data = []
        for day in data.details:
            day_dict = day.model_dump()
            if day_dict.get("date"):
                day_dict["date"] = day_dict["date"].isoformat()
            if day_dict.get("attachments"):
                for att in day_dict["attachments"]:
                    if att.get("created_at"):
                        att["created_at"] = att["created_at"].isoformat()
            details_data.append(day_dict)
        itinerary.details = details_data

    await db.commit()
    await db.refresh(itinerary)
    return ResponseModel(data=itinerary)


@router.delete("/{itinerary_id}", response_model=ResponseModel)
async def delete_itinerary(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Itinerary).where(
            Itinerary.id == itinerary_id,
            Itinerary.created_by == current_user.id,
        )
    )
    itinerary = result.scalar_one_or_none()
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found",
        )
    await db.delete(itinerary)
    await db.commit()
    return ResponseModel(message="Itinerary deleted successfully")


@router.post("/{itinerary_id}/share", response_model=ResponseModel[dict])
async def generate_share_token(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Itinerary).where(
            Itinerary.id == itinerary_id,
            Itinerary.created_by == current_user.id,
        )
    )
    itinerary = result.scalar_one_or_none()
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found",
        )
    if not itinerary.share_token:
        itinerary.share_token = secrets.token_urlsafe(32)
        await db.commit()
    return ResponseModel(data={"share_token": itinerary.share_token})


@router.get("/share/{token}", response_model=ResponseModel[ItinerarySchema])
async def get_shared_itinerary(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Itinerary).where(Itinerary.share_token == token)
    )
    itinerary = result.scalar_one_or_none()
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found",
        )
    return ResponseModel(data=itinerary)
