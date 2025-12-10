# app/api/impacts.py

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models import ImpactCaseSchema
from app.repositories.impact_repository import ImpactRepository

router = APIRouter()


def get_repository() -> ImpactRepository:
    """
    Prosta dependency injection dla repozytorium.
    W przyszłości można tu dodać np. cache, konfigurację itd.
    """
    return ImpactRepository()


@router.get(
    "/",
    response_model=List[ImpactCaseSchema],
    summary="Lista impactów",
    description=(
        "Zwraca listę opisów wpływu (impactów) z bazy MongoDB, "
        "z opcjonalnym filtrowaniem po institution_uuid i discipline_code."
    ),
)
async def list_impacts_endpoint(
    skip: int = Query(0, ge=0, description="Offset (liczba rekordów do pominięcia)"),
    limit: int = Query(50, gt=0, le=200, description="Liczba rekordów do zwrócenia"),
    institution_uuid: Optional[str] = Query(
        None,
        description="Filtr: UUID instytucji (institution_uuid).",
    ),
    discipline_code: Optional[str] = Query(
        None,
        description="Filtr: kod dyscypliny (discipline_code).",
    ),
    repo: ImpactRepository = Depends(get_repository),
) -> List[ImpactCaseSchema]:
    return await repo.list_impacts(
        skip=skip,
        limit=limit,
        institution_uuid=institution_uuid,
        discipline_code=discipline_code,
    )


@router.get(
    "/{impact_uuid}",
    response_model=ImpactCaseSchema,
    summary="Single impact description (use impact_uuid)",
)
async def get_impact_endpoint(
    impact_uuid: str,
    repo: ImpactRepository = Depends(get_repository),
) -> ImpactCaseSchema:
    impact = await repo.get_by_impact_uuid(impact_uuid)
    if not impact:
        raise HTTPException(status_code=404, detail="Impact not found")

    return impact
