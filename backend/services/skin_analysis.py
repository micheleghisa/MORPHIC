"""
GLOWUP AI — Skin Analysis Service
Analisi della pelle: texture, pigmentazione, rughe, occhiaie, acne
"""
import numpy as np
import cv2
from skimage.feature import graycomatrix, graycoprops
from skimage.filters import sobel, gabor
from typing import Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class SkinMetrics:
    """Risultato analisi pelle"""
    texture_score: float          # 0-100, 100 = pelle liscia perfetta
    roughness: float              # Indice rugosità
    pigmentation_score: float     # 0-100, 100 = tono uniforme
    hyperpigmentation_spots: int  # Numero macchie scure rilevate
    redness_score: float          # 0-100, 100 = nessun rossore (bassa rosacea)
    wrinkle_score: float          # 0-100, 100 = nessuna ruga
    wrinkle_density: float        # Densità rughe per cm²
    darkness_under_eyes: float    # Intensità occhiaie 0-100
    pore_score: float             # 0-100, 100 = pori poco visibili
    overall_skin_health: float    # 0-100 composito


# ─── REGIONI DEL VISO ───

# Bounding box approssimative come frazione delle dimensioni immagine
# Assumiamo che le immagini siano centrate e normalizzate

FACE_REGIONS = {
    "forehead":    (0.25, 0.10, 0.75, 0.30),
    "t_zone":      (0.35, 0.28, 0.65, 0.42),
    "left_cheek":  (0.10, 0.35, 0.35, 0.60),
    "right_cheek": (0.65, 0.35, 0.90, 0.60),
    "nose":        (0.40, 0.30, 0.60, 0.55),
    "under_eyes":  (0.20, 0.32, 0.80, 0.42),
    "chin":        (0.35, 0.60, 0.65, 0.85),
    "jawline":     (0.20, 0.55, 0.80, 0.70),
}


def extract_region(image: np.ndarray, region_name: str) -> np.ndarray:
    """Estrae una regione facciale dall'immagine usando bounding box"""
    h, w = image.shape[:2]
    x1, y1, x2, y2 = FACE_REGIONS.get(region_name, (0.2, 0.2, 0.8, 0.8))
    x1, x2 = int(x1 * w), int(x2 * w)
    y1, y2 = int(y1 * h), int(y2 * h)
    return image[y1:y2, x1:x2]


# ─── ANALISI TEXTURE (GLCM) ───

def analyze_texture(gray_region: np.ndarray) -> Tuple[float, float]:
    """
    Analizza texture della pelle usando GLCM (Gray-Level Co-occurrence Matrix).
    Ritorna (texture_score, roughness)
    """
    if gray_region.size == 0:
        return 50.0, 0.5

    # Riduci a 8-bit per GLCM
    gray = (gray_region * 255).astype(np.uint8) if gray_region.max() <= 1 else gray_region

    # GLCM con offset di 1 pixel
    glcm = graycomatrix(gray, distances=[1], angles=[0], levels=256, symmetric=True, normed=True)

    contrast = float(graycoprops(glcm, 'contrast')[0, 0])
    homogeneity = float(graycoprops(glcm, 'homogeneity')[0, 0])
    energy = float(graycoprops(glcm, 'energy')[0, 0])
    correlation = float(graycoprops(glcm, 'correlation')[0, 0])

    # Texture score: combina contrast (basso=liscio) e homogeneity (alto=liscio)
    texture_score = (homogeneity * 60) + (energy * 30) + (max(0, 1 - contrast / 100) * 10)
    texture_score = min(100, max(0, texture_score))

    roughness = contrast / 50  # Normalizzato

    return round(texture_score, 1), round(roughness, 4)


# ─── ANALISI PIGMENTAZIONE ───

def analyze_pigmentation(hsv_region: np.ndarray) -> Tuple[float, int]:
    """
    Analizza uniformità pigmentazione nel canale V (value).
    Ritorna (pigmentation_score, spot_count)
    """
    if hsv_region.size == 0:
        return 50.0, 0

    value = hsv_region[:, :, 2]  # Canale V di HSV

    # Calcola varianza locale come indicatore di disuniformità
    mean_v = np.mean(value)
    std_v = np.std(value)

    # Spot detection: aree significativamente più scure del vicinato
    blurred = cv2.GaussianBlur(value, (15, 15), 0)
    diff = cv2.absdiff(value, blurred)
    _, spots = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)

    num_spots = int(np.sum(spots > 0) / 25)  # cluster di 5x5

    # Score: bassa varianza = alta uniformità
    score = 100 - (std_v * 2)
    score = max(0, min(100, score))
    # Penalità per numero spot
    score = max(0, score - num_spots * 0.5)

    return round(score, 1), num_spots


# ─── ANALISI ROSSORE (ROSACEA ERITEMA) ───

def analyze_redness(hsv_region: np.ndarray) -> float:
    """
    Analizza rossore cutaneo nel canale H (hue) di HSV.
    Score alto = poco rossore (cute sana)
    """
    if hsv_region.size == 0:
        return 50.0

    hue = hsv_region[:, :, 0]  # 0-180 in OpenCV
    saturation = hsv_region[:, :, 1]

    # Il rosso è intorno a 0 e 180 in HSV
    red_mask = (hue < 10) | (hue > 170)
    red_pixels = np.sum(red_mask & (saturation > 50))
    total_pixels = hue.size

    redness_ratio = red_pixels / total_pixels

    # Score: bassa percentuale rosso = alto score
    score = 100 - (redness_ratio * 200)
    score = max(0, min(100, score))

    return round(score, 1)


# ─── ANALISI ONDULAZIONI / RUGHE ───

def analyze_wrinkles(gray_region: np.ndarray) -> Tuple[float, float]:
    """
    Rileva rughe usando il filtro di Gabor.
    Ritorna (wrinkle_score, wrinkle_density)
    """
    if gray_region.size == 0:
        return 50.0, 0.0

    gray = (gray_region * 255).astype(np.uint8) if gray_region.max() <= 1 else gray_region

    # Filtro Gabor per rilevare linee sottili
    gabor_real, _ = gabor(gray, frequency=0.3, theta=0)
    gabor_real2, _ = gabor(gray, frequency=0.3, theta=np.pi / 4)
    gabor_real3, _ = gabor(gray, frequency=0.3, theta=np.pi / 2)
    gabor_real4, _ = gabor(gray, frequency=0.3, theta=3 * np.pi / 4)

    combined = np.maximum.reduce([
        np.abs(gabor_real),
        np.abs(gabor_real2),
        np.abs(gabor_real3),
        np.abs(gabor_real4),
    ])

    # Percentuale di pixel che mostrano pattern di rughe
    _, binary = cv2.threshold((combined * 255).astype(np.uint8), 30, 255, cv2.THRESH_BINARY)
    wrinkle_ratio = np.sum(binary > 0) / binary.size

    wrinkle_density = round(wrinkle_ratio * 100, 4)  # % area con rughe

    # Score: meno rughe = score più alto
    score = 100 - wrinkle_density * 5
    score = max(0, min(100, score))

    return round(score, 1), wrinkle_density


# ─── ANALISI OCCHIAIE ───

def analyze_under_eyes(hsv_region: np.ndarray) -> float:
    """
    Analizza occhiaie misurando l'intensità scura sotto gli occhi.
    Ritorna intensità occhiaie (0-100, alto = occhiaie marcate)
    """
    if hsv_region.size == 0:
        return 50.0

    value = hsv_region[:, :, 2]  # Canale V
    saturation = hsv_region[:, :, 1]  # Canale S

    # Occhiaie = V basso + S basso
    darkness_score = (255 - np.mean(value))
    low_sat = np.mean(saturation) < 80

    if low_sat:
        darkness_score *= 1.3

    darkness_score = min(100, max(0, darkness_score / 2.55))

    return round(darkness_score, 1)


# ─── ANALISI PORI ───

def analyze_pores(gray_region: np.ndarray) -> float:
    """
    Analizza visibilità dei pori usando edge detection locale.
    Score alto = pori poco visibili.
    """
    if gray_region.size == 0:
        return 50.0

    gray = (gray_region * 255).astype(np.uint8) if gray_region.max() <= 1 else gray_region

    # Edge detection per rilevare micro-buchi (pori)
    edges = sobel(gray)

    # Più edge localizzati = più pori visibili
    pore_indicator = np.std(edges)

    score = 100 - pore_indicator * 3
    score = max(0, min(100, score))

    return round(score, 1)


# ─── ANALISI COMPLETA PELLE ───

def analyze_skin(image: np.ndarray) -> SkinMetrics:
    """
    Esegue analisi completa della pelle su una immagine contenente un volto.
    """
    # Converti in HSV e grayscale
    if len(image.shape) == 3:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        gray_uint = (gray * 255).astype(np.uint8)
    else:
        hsv = None
        gray = image.astype(np.float32) / 255.0
        gray_uint = (gray * 255).astype(np.uint8)

    # Analizza ogni regione
    cheek_r = extract_region(image, "right_cheek")
    cheek_l = extract_region(image, "left_cheek")
    forehead = extract_region(image, "forehead")
    nose = extract_region(image, "nose")
    under_eyes = extract_region(image, "under_eyes")

    # Convert regions to grayscale
    def to_gray(r):
        if len(r.shape) == 3:
            return cv2.cvtColor(r, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        return r.astype(np.float32) / 255.0

    def to_hsv(r):
        if len(r.shape) == 3:
            return cv2.cvtColor(r, cv2.COLOR_BGR2HSV)
        return None

    # Texture (media guance + fronte)
    texture_scores = []
    roughness_scores = []
    for region_gray in [to_gray(cheek_r), to_gray(cheek_l), to_gray(forehead)]:
        ts, rough = analyze_texture(region_gray)
        texture_scores.append(ts)
        roughness_scores.append(rough)

    avg_texture = np.mean(texture_scores)
    avg_roughness = np.mean(roughness_scores)

    # Pigmentazione (guance)
    pig_scores = []
    spot_counts = []
    for region_hsv in [to_hsv(cheek_r), to_hsv(cheek_l)]:
        if region_hsv is not None:
            ps, sc = analyze_pigmentation(region_hsv)
            pig_scores.append(ps)
            spot_counts.append(sc)

    avg_pigmentation = np.mean(pig_scores) if pig_scores else 50
    total_spots = int(np.sum(spot_counts))

    # Rossore (guance + naso)
    redness_scores = []
    for rhsv in [to_hsv(cheek_r), to_hsv(cheek_l), to_hsv(nose)]:
        if rhsv is not None:
            redness_scores.append(analyze_redness(rhsv))
    avg_redness = np.mean(redness_scores) if redness_scores else 50

    # Rughe (fronte + contorno occhi)
    under_eyes_gray = to_gray(under_eyes)
    wrinkle_scores_forehead, wdens1 = analyze_wrinkles(to_gray(forehead))
    wrinkle_scores_eyes, wdens2 = analyze_wrinkles(under_eyes_gray)
    avg_wrinkle_score = (wrinkle_scores_forehead + wrinkle_scores_eyes) / 2
    avg_wrinkle_density = (wdens1 + wdens2) / 2

    # Occhiaie
    under_eyes_hsv = to_hsv(under_eyes)
    dark = analyze_under_eyes(under_eyes_hsv) if under_eyes_hsv is not None else 50

    # Pori (naso)
    pore_score = analyze_pores(to_gray(nose))

    # Overall
    overall = np.mean([
        avg_texture,
        avg_pigmentation,
        avg_redness,
        avg_wrinkle_score,
        pore_score,
    ])

    return SkinMetrics(
        texture_score=round(avg_texture, 1),
        roughness=round(avg_roughness, 4),
        pigmentation_score=round(avg_pigmentation, 1),
        hyperpigmentation_spots=total_spots,
        redness_score=round(avg_redness, 1),
        wrinkle_score=round(avg_wrinkle_score, 1),
        wrinkle_density=round(avg_wrinkle_density, 4),
        darkness_under_eyes=round(dark, 1),
        pore_score=round(pore_score, 1),
        overall_skin_health=round(overall, 1),
    )
