"""
GLOWUP AI — Visualization Service
Face morphing geometrico + inpainting localizzato per preview prima/dopo.
Accetta i compromessi dichiarati: qualità inferiore a QOVES ma funzionale.
"""
import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
from PIL import Image
import io


@dataclass
class MorphConfig:
    """Configurazione per una trasformazione morfologica."""
    landmark_indices: List[int]      # Punti MediaPipe da spostare
    displacement: List[Tuple[float, float]]  # (dx, dy) in coordinate normalizzate
    description: str                 # Nome della modifica


# ─── TRASFORMAZIONI PREDEFINITE ───

# Basate su indici MediaPipe Face Mesh (vedi face_analysis.py)
MORPH_TRANSFORMS = {
    "straighten_eyebrows": MorphConfig(
        landmark_indices=[70, 63, 105, 66, 107, 300, 293, 334, 296, 336],
        displacement=[(0, -0.03), (0, -0.02), (0, -0.01), (0, 0.015), (0, 0.01),
                      (0, -0.03), (0, 0.01), (0, 0.015), (0, -0.005), (0, -0.02)],
        description="Eyebrows aligned and lifted"
    ),
    "reduce_nasal_width": MorphConfig(
        landmark_indices=[98, 327, 48, 331],
        displacement=[(0.02, 0), (-0.02, 0), (0.015, 0), (-0.015, 0)],
        description="Nose width refined"
    ),
    "enhance_jawline": MorphConfig(
        landmark_indices=[58, 288, 172, 397],
        displacement=[(0.03, -0.02), (-0.03, -0.02), (0.025, 0.015), (-0.025, 0.015)],
        description="Jawline definition enhanced"
    ),
    "lip_fullness": MorphConfig(
        landmark_indices=[13, 14, 0, 17],
        displacement=[(0, -0.025), (0, 0.025), (0, -0.015), (0, 0.015)],
        description="Lip fullness adjusted"
    ),
    "chin_projection": MorphConfig(
        landmark_indices=[152, 140, 377],
        displacement=[(0, 0.05), (0.02, 0.03), (-0.02, 0.03)],
        description="Chin projection improved"
    ),
    "canthal_tilt_fix": MorphConfig(
        landmark_indices=[33, 133, 362, 263],
        displacement=[(0, -0.02), (0, 0.02), (0, -0.02), (0, 0.02)],
        description="Eye tilt adjusted"
    ),
}


# ─── FACE MORPHING ───

def apply_morph(
    image: np.ndarray,
    landmarks: np.ndarray,  # (478, 2) coordinate pixel
    transform_name: str,
    intensity: float = 1.0,  # 0.0 - 1.0
) -> np.ndarray:
    """
    Applica una trasformazione morfologica al viso.
    Usa triangolazione di Delaunay + affine warp.
    """
    if transform_name not in MORPH_TRANSFORMS:
        return image

    config = MORPH_TRANSFORMS[transform_name]
    h, w = image.shape[:2]

    # Source points: tutti i landmark
    src_points = landmarks.copy()

    # Destination points: landmark modificati
    dst_points = landmarks.copy()

    for idx, (dx, dy) in zip(config.landmark_indices, config.displacement):
        if idx < len(dst_points):
            # Applica displacement normalizzato moltiplicato per dimensione immagine
            dst_points[idx][0] += dx * w * intensity
            dst_points[idx][1] += dy * h * intensity

    # Crea mesh triangolare usando Delaunay su punti medi
    # (usiamo i landmark dell'occhio, naso, bocca, mascella per triangolare)
    hull_indices = list(range(0, 478, 10))  # Un landmark ogni 10 per performance

    # Assicurati che i punti non escano dai bordi
    src_points = np.clip(src_points, 0, [w - 1, h - 1])
    dst_points = np.clip(dst_points, 0, [w - 1, h - 1])

    try:
        # Triangolazione di Delaunay
        from scipy.spatial import Delaunay
        tri = Delaunay(src_points[hull_indices])

        # Applica affine warp per ogni triangolo
        warped = np.zeros_like(image)
        mask = np.zeros((h, w), dtype=np.float32)

        src_pts = src_points.astype(np.float32)
        dst_pts = dst_points.astype(np.float32)

        for simplex in tri.simplices:
            # Ottieni i 3 punti del triangolo
            src_tri = src_pts[hull_indices[simplex]]
            dst_tri = dst_pts[hull_indices[simplex]]

            # Matrice di trasformazione affine
            warp_mat = cv2.getAffineTransform(src_tri, dst_tri)

            # Crea maschera per questo triangolo
            tri_mask = np.zeros((h, w), dtype=np.uint8)
            pts_int = src_tri.astype(np.int32)
            cv2.fillConvexPoly(tri_mask, pts_int, 255)

            # Warp
            warped_tri = cv2.warpAffine(
                image, warp_mat, (w, h),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT
            )

            # Applica solo nella maschera
            tri_mask_3ch = cv2.cvtColor(tri_mask, cv2.COLOR_GRAY2BGR) / 255.0
            warped = (warped * (1 - tri_mask_3ch) + warped_tri * tri_mask_3ch).astype(np.uint8)

        return warped

    except Exception:
        # Fallback: ritorna immagine originale se il morphing fallisce
        return image


# ─── INPAINTING LOCALIZZATO ───

def inpaint_skin(
    image: np.ndarray,
    mask: np.ndarray,  # Maschera binaria delle aree da migliorare
    method: str = "telea",
) -> np.ndarray:
    """
    Migliora aree cutanee localizzate usando inpainting.
    Per rughe, macchie, imperfezioni.
    """
    if mask is None or np.sum(mask) == 0:
        return image

    # Inpainting: riempie le aree mascherate usando il contesto circostante
    if method == "telea":
        return cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    else:
        return cv2.inpaint(image, mask, inpaintRadius=5, flags=cv2.INPAINT_NS)


def create_blemish_mask(
    image: np.ndarray,
    threshold: int = 40,
) -> np.ndarray:
    """
    Crea una maschera per imperfezioni cutanee (macchie, acne).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (21, 21), 0)
    diff = cv2.absdiff(gray, blurred)

    # Le imperfezioni sono deviazioni locali dal vicinato sfocato
    _, mask = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

    # Pulisci rumore
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    return mask


# ─── COMPOSIZIONE BEFORE/AFTER ───

def create_before_after_composite(
    before: np.ndarray,
    after: np.ndarray,
    label_before: str = "Before",
    label_after: str = "After",
) -> np.ndarray:
    """
    Crea immagine side-by-side prima/dopo con etichette.
    """
    h, w = before.shape[:2]

    # Canvas: 2 immagini affiancate + spazio per etichette
    label_height = 40
    canvas = np.ones((h + label_height, w * 2, 3), dtype=np.uint8) * 255

    # Posiziona immagini
    canvas[label_height:label_height + h, 0:w] = before
    canvas[label_height:label_height + h, w:w * 2] = after

    # Aggiungi etichette
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(canvas, label_before, (w // 2 - 40, 30), font, 0.7, (0, 0, 0), 2)
    cv2.putText(canvas, label_after, (w + w // 2 - 30, 30), font, 0.7, (0, 0, 0), 2)

    # Linea divisoria centrale
    cv2.line(canvas, (w, label_height), (w, h + label_height), (200, 200, 200), 2)

    return canvas


# ─── GENERAZIONE COMPLETA VISUALIZZAZIONI ───

def generate_all_visualizations(
    image: np.ndarray,
    landmarks: np.ndarray,
) -> Dict[str, bytes]:
    """
    Genera tutte le visualizzazioni prima/dopo e le ritorna come bytes PNG.
    """
    results = {}

    # 1. Trasformazioni morfologiche
    for transform_name in MORPH_TRANSFORMS:
        try:
            morphed = apply_morph(image, landmarks, transform_name, intensity=0.8)
            composite = create_before_after_composite(
                image, morphed,
                label_before="Current",
                label_after=MORPH_TRANSFORMS[transform_name].description
            )
            _, buffer = cv2.imencode('.png', composite)
            results[f"morph_{transform_name}"] = buffer.tobytes()
        except Exception as e:
            logger = __import__('structlog').get_logger()
            logger.warning(f"visualization_failed", transform=transform_name, error=str(e))

    # 2. Skin enhancement (inpainting imperfezioni)
    try:
        blemish_mask = create_blemish_mask(image)
        skin_enhanced = inpaint_skin(image, blemish_mask)
        composite_skin = create_before_after_composite(
            image, skin_enhanced,
            label_before="Current Skin",
            label_after="Enhanced Skin Texture"
        )
        _, buffer = cv2.imencode('.png', composite_skin)
        results["skin_enhancement"] = buffer.tobytes()
    except Exception:
        pass

    # 3. Composite finale (tutte le modifiche combinate)
    try:
        combined = image.copy()
        for transform_name in MORPH_TRANSFORMS:
            combined = apply_morph(combined, landmarks, transform_name, intensity=0.7)

        blemish_mask = create_blemish_mask(combined)
        combined = inpaint_skin(combined, blemish_mask)

        composite = create_before_after_composite(
            image, combined,
            label_before="Current",
            label_after="Full Glow-Up Preview"
        )
        _, buffer = cv2.imencode('.png', composite)
        results["full_glowup"] = buffer.tobytes()
    except Exception:
        pass

    return results
