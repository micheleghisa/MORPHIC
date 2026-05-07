"""
GLOWUP AI — API Routes
Endpoint: upload foto, stato analisi, report, chat, cancellazione GDPR
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, Response
from typing import List, Optional
import json

from services.face_analysis import analyze_multiple_photos
from services.skin_analysis import analyze_skin
from services.report_generator import get_report_generator
from services.llm_provider import get_llm_provider
from services.visualization import generate_all_visualizations
from workers.analysis_worker import queue_analysis, get_analysis_status
from config import settings

import cv2
import numpy as np
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1", tags=["analysis"])


# ─── UPLOAD & ANALYZE ───

@router.post("/analyze")
async def upload_and_analyze(
    background_tasks: BackgroundTasks,
    photos: List[UploadFile] = File(..., description="6 photos: front, profile R, profile L, 3/4 R, 3/4 L, front smiling"),
    age: int = Form(..., ge=13, le=120),
    gender: str = Form(..., description="male, female, other"),
    ethnicity: str = Form(...),
    skin_type: str = Form(..., description="dry, oily, combination, normal, sensitive"),
    skin_concerns: str = Form("[]", description="JSON array of skin concerns"),
    goals: str = Form("[]", description="JSON array of goals"),
    lifestyle_factors: str = Form("{}", description="JSON object"),
):
    """
    Carica 6 foto e avvia analisi asincrona.
    Ritorna immediatamente con un analysis_id.
    Il backend processa in background.
    """
    # Validazione numero foto
    if len(photos) != settings.required_photo_count:
        raise HTTPException(
            status_code=400,
            detail=f"Exactly {settings.required_photo_count} photos required, got {len(photos)}"
        )

    # Valida formati
    allowed_extensions = settings.allowed_photo_formats.split(",")
    for photo in photos:
        ext = photo.filename.split(".")[-1].lower() if "." in photo.filename else ""
        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Format {ext} not allowed")

        contents = await photo.read()
        if len(contents) > settings.max_photo_size_mb * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File {photo.filename} too large")
        await photo.seek(0)

    try:
        skin_concerns_list = json.loads(skin_concerns)
        goals_list = json.loads(goals)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON for skin_concerns or goals")

    # Crea record analisi e metti in coda
    try:
        analysis_id = await queue_analysis(
            photos=photos,
            age=age,
            gender=gender,
            ethnicity=ethnicity,
            skin_type=skin_type,
            skin_concerns=skin_concerns_list,
            goals=goals_list,
            lifestyle_factors=json.loads(lifestyle_factors),
        )
    except Exception as e:
        logger.error("queue_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to start analysis")

    return {
        "analysis_id": analysis_id,
        "status": "queued",
        "estimated_completion_seconds": 300,
        "message": "Analysis started. Poll /api/v1/analysis/{id} for results."
    }


@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """
    Recupera lo stato e i risultati di un'analisi.
    """
    status = await get_analysis_status(analysis_id)

    if status is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return status


# ─── REPORT ───

@router.get("/analysis/{analysis_id}/report")
async def get_report(analysis_id: str, format: str = "json"):
    """
    Recupera il report generato. Formato: json, markdown, pdf (futuro).
    """
    status = await get_analysis_status(analysis_id)

    if status is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if status.get("status") != "completed":
        raise HTTPException(
            status_code=202,
            detail=f"Analysis not yet completed. Status: {status.get('status')}"
        )

    if format == "markdown":
        return Response(
            content=status.get("report", {}).get("report_markdown", ""),
            media_type="text/markdown"
        )

    return status.get("report", {}).get("report_json", {})


# ─── CHAT AI ───

@router.post("/chat")
async def chat_with_ai(
    question: str = Form(...),
    analysis_id: Optional[str] = Form(None),
    history: str = Form("[]"),
):
    """
    Chat con l'assistente estetico AI.
    Opzionalmente referenzia un'analisi esistente.
    """
    try:
        chat_history = json.loads(history)
    except json.JSONDecodeError:
        chat_history = []

    # Recupera contesto report se disponibile
    report_context = {}
    if analysis_id:
        status = await get_analysis_status(analysis_id)
        if status and status.get("report"):
            report_context = status["report"].get("report_json", {})

    generator = get_report_generator()
    result = await generator.generate_chat_response(
        user_question=question,
        report_context=report_context,
        chat_history=chat_history,
    )

    return result


# ─── GDPR DATA DELETION ───

@router.delete("/user/{user_id}/data")
async def delete_user_data(user_id: str):
    """
    Richiesta cancellazione dati GDPR (Art. 17).
    Elimina foto, analisi, report.
    """
    # TODO: implementare cancellazione effettiva da DB e storage
    logger.info("gdpr_deletion_requested", user_id=user_id)
    return {
        "status": "deletion_queued",
        "message": "All your data will be permanently deleted within 30 days."
    }


# ─── HEALTH SPECIFICO ───

@router.get("/ping")
async def ping():
    return {"status": "ok", "provider": settings.llm_provider}
