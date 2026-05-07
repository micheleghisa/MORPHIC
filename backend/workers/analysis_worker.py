"""
GLOWUP AI — Analysis Worker
Processa le analisi in modo asincrono. Sostituisce Celery con una coda Redis semplice.
In produzione: usare Celery + Redis o BullMQ.
"""
import json
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime
import structlog

from services.face_analysis import analyze_face
from services.skin_analysis import analyze_skin
from services.report_generator import get_report_generator
from services.visualization import generate_all_visualizations
from config import settings

import cv2
import numpy as np
import uuid

logger = structlog.get_logger()

# ─── IN-MEMORY STORE (da sostituire con Redis + DB) ───

_analyses_store: Dict[str, Dict[str, Any]] = {}


async def queue_analysis(
    photos: list,
    age: int,
    gender: str,
    ethnicity: str,
    skin_type: str,
    skin_concerns: list,
    goals: list,
    lifestyle_factors: dict,
) -> str:
    """
    Mette in coda un'analisi e ritorna l'ID.
    Lancia l'elaborazione in background.
    """
    analysis_id = str(uuid.uuid4())

    # Leggi tutte le foto in memoria
    photo_data = []
    for photo in photos:
        contents = await photo.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        photo_data.append(img)

    # Salva metadati
    _analyses_store[analysis_id] = {
        "id": analysis_id,
        "status": "queued",
        "age": age,
        "gender": gender,
        "ethnicity": ethnicity,
        "skin_type": skin_type,
        "skin_concerns": skin_concerns,
        "goals": goals,
        "photo_data": photo_data,
        "created_at": datetime.utcnow().isoformat(),
        "report": None,
        "error": None,
    }

    # Avvia processamento in background
    asyncio.create_task(_process_analysis(analysis_id))

    return analysis_id


async def get_analysis_status(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Recupera lo stato di un'analisi."""
    if analysis_id not in _analyses_store:
        return None

    data = _analyses_store[analysis_id].copy()
    # Rimuovi dati foto dalla risposta (troppo grandi)
    data.pop("photo_data", None)
    return data


async def _process_analysis(analysis_id: str):
    """
    Pipeline completa di analisi in background.
    1. Face Landmark Extraction
    2. Skin Analysis
    3. Metriche aggregate
    4. Report LLM
    5. Visualizzazioni
    """
    logger.info("analysis_started", analysis_id=analysis_id)

    try:
        data = _analyses_store[analysis_id]
        photos = data["photo_data"]
        start_time = time.time()

        # ─── STEP 1: Analisi facciale ───
        _analyses_store[analysis_id]["status"] = "processing"
        logger.info("step_face_analysis", analysis_id=analysis_id)

        facial_results = []
        skin_metrics = None

        for i, img in enumerate(photos):
            # Analisi landmark
            face_analysis = analyze_face(img)
            if face_analysis:
                facial_results.append({
                    "symmetry": face_analysis.symmetry.__dict__,
                    "proportions": face_analysis.proportions.__dict__,
                    "face_shape": face_analysis.face_shape,
                    "masculinity_femininity": face_analysis.masculinity_femininity,
                    "canthal_tilt": face_analysis.canthal_tilt,
                    "golden_ratios": face_analysis.perceived_golden_ratios,
                })

            # Analisi pelle solo sulla foto frontale (index 0)
            if i == 0:
                skin = analyze_skin(img)
                skin_metrics = skin.__dict__ if skin else {}

        if not facial_results:
            _analyses_store[analysis_id]["status"] = "failed"
            _analyses_store[analysis_id]["error"] = "No face detected in any photo"
            logger.error("no_face_detected", analysis_id=analysis_id)
            return

        # Usa la foto frontale (prima) come riferimento
        primary_analysis = facial_results[0]

        # ─── STEP 2: Aggregazione dati ───
        biometric_data = {
            "symmetry": primary_analysis.get("symmetry"),
            "proportions": primary_analysis.get("proportions"),
            "face_shape": primary_analysis.get("face_shape"),
            "masculinity_femininity_score": primary_analysis.get("masculinity_femininity"),
            "canthal_tilt_degrees": primary_analysis.get("canthal_tilt"),
            "golden_ratio_proximity": primary_analysis.get("golden_ratios"),
        }

        # ─── STEP 3: Report LLM ───
        logger.info("step_report_generation", analysis_id=analysis_id)

        generator = get_report_generator()
        report = await generator.generate_report(
            age=data["age"],
            gender=data["gender"],
            ethnicity=data["ethnicity"],
            skin_type=data["skin_type"],
            skin_concerns=data.get("skin_concerns", []),
            goals=data.get("goals", []),
            biometric_data=biometric_data,
            skin_data=skin_metrics or {},
        )

        # ─── STEP 4: Visualizzazioni ───
        logger.info("step_visualizations", analysis_id=analysis_id)
        visualizations = {}

        try:
            front_photo = photos[0]
            import base64

            # STEP 4a: Fal.ai AI Glow-Up (before/after transformation)
            try:
                from services.ai_visualization import generate_before_after_composite
                ai_results = await generate_before_after_composite(
                    front_photo,
                    gender=data.get("gender", "male"),
                    age=int(data.get("age", 25)),
                    skin_concerns=data.get("skin_concerns", []),
                    goals=data.get("goals", []),
                )
                for key, img_bytes in ai_results.items():
                    visualizations[key] = base64.b64encode(img_bytes).decode("utf-8")
                logger.info("ai_visualizations_done", count=len(ai_results))
            except Exception as e:
                logger.warning("ai_visualizations_failed", error=str(e))

            # STEP 4b: Fallback morphing geometrico
            from services.face_analysis import extract_landmarks
            landmarks = extract_landmarks(front_photo)
            if landmarks:
                viz_results = generate_all_visualizations(front_photo, landmarks.points_2d)
                for key, img_bytes in viz_results.items():
                    if key not in visualizations:
                        visualizations[key] = base64.b64encode(img_bytes).decode("utf-8")
        except Exception as e:
            logger.warning("visualizations_failed", error=str(e))

        # ─── STEP 5: Salva risultati ───
        processing_time = time.time() - start_time

        # Include original front photo for before/after slider
        _, orig_buffer = cv2.imencode('.png', photos[0])
        original_photo_b64 = base64.b64encode(orig_buffer).decode("utf-8")

        _analyses_store[analysis_id].update({
            "status": "completed",
            "biometric_data": biometric_data,
            "skin_metrics": skin_metrics,
            "report": {
                "report_markdown": report["report_markdown"],
                "report_json": report["report_json"],
                "provider": report["provider"],
            },
            "visualizations": visualizations,
            "original_photo": original_photo_b64,
            "processing_time_seconds": round(processing_time, 1),
            "confidence_score": 0.85,  # Stima; migliorabile con validazione
            "completed_at": datetime.utcnow().isoformat(),
        })

        logger.info(
            "analysis_completed",
            analysis_id=analysis_id,
            processing_time=round(processing_time, 1),
            provider=report["provider"],
        )

    except Exception as e:
        logger.error("analysis_failed", analysis_id=analysis_id, error=str(e))
        _analyses_store[analysis_id]["status"] = "failed"
        _analyses_store[analysis_id]["error"] = str(e)
