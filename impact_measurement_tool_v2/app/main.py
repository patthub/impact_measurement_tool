# app/main.py

from __future__ import annotations

import logging

from fastapi import FastAPI

from app.api.impacts import router as impacts_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="imeto API",
    version="0.1.0",
    description=(
        "Read impacts retrieved from radon api"
    ),
)


@app.get("/health", summary="Health check")
async def health() -> dict:
    return {"status": "ok"}


# Rejestrujemy router z endpointami dla impactów
app.include_router(impacts_router, prefix="/impacts", tags=["impacts"])
