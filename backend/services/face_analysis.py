"""
GLOWUP AI — Servizio di Analisi Facciale
Usa MediaPipe Face Mesh per estrarre 478 landmark 3D e calcolare metriche estetiche.
"""
import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import math


# ─── DATA CLASSES ───

@dataclass
class FaceLandmarks:
    """Landmark facciali completi da una foto"""
    points_3d: np.ndarray  # (478, 3) coordinate x,y,z normalizzate
    points_2d: np.ndarray  # (478, 2) coordinate pixel
    image_width: int
    image_height: int
    confidence: float

@dataclass
class SymmetryMetrics:
    """Metriche di simmetria facciale"""
    overall_symmetry: float       # 0-100
    eye_symmetry: float           # 0-100
    brow_symmetry: float          # 0-100
    nose_symmetry: float          # 0-100
    lip_symmetry: float           # 0-100
    jaw_symmetry: float           # 0-100
    midface_deviation_mm: float   # Deviazione linea mediana in mm

@dataclass
class ProportionMetrics:
    """Metriche di proporzioni facciali"""
    upper_third_ratio: float      # Fronte rispetto a altezza totale
    middle_third_ratio: float     # Naso
    lower_third_ratio: float      # Mascella/mento
    facial_index: float           # Altezza/larghezza viso
    intercanthal_distance_ratio: float  # Distanza occhi / larghezza viso
    nasal_width_ratio: float      # Larghezza naso / larghezza viso
    mouth_width_ratio: float      # Larghezza bocca / larghezza viso
    chin_projection_ratio: float  # Proiezione mento
    jaw_angle: float              # Angolo mandibolare
    gonial_angle: float           # Angolo goniale
    bigonial_width_ratio: float   # Larghezza bigoniale / larghezza bizigomatica

@dataclass
class FacialAnalysis:
    """Risultato completo dell'analisi facciale"""
    symmetry: SymmetryMetrics
    proportions: ProportionMetrics
    face_shape: str
    masculinity_femininity: float  # >50 = maschile, <50 = femminile (approssimato)
    canthal_tilt: float           # Angolo inclinazione occhi
    brow_position: float          # Altezza sopracciglia normalizzata
    perceived_golden_ratios: Dict[str, float]  # Rapporti aurei per varie feature
    raw_landmarks: List[FaceLandmarks]


# ─── INDICI MEDIAPIPE PUNTI CHIAVE ───
# MediaPipe Face Mesh ha 478 punti. Qui i più importanti per l'estetica.

class LandmarkIndices:
    """Indici dei landmark MediaPipe più rilevanti per l'analisi estetica"""
    # Occhi
    LEFT_EYE_OUTER = 33
    LEFT_EYE_INNER = 133
    RIGHT_EYE_INNER = 362
    RIGHT_EYE_OUTER = 263
    LEFT_EYE_TOP = 159
    LEFT_EYE_BOTTOM = 145
    RIGHT_EYE_TOP = 386
    RIGHT_EYE_BOTTOM = 374

    # Sopracciglia
    LEFT_BROW_OUTER = 70
    LEFT_BROW_INNER = 107
    RIGHT_BROW_INNER = 336
    RIGHT_BROW_OUTER = 300

    # Naso
    NOSE_TIP = 1
    NOSE_BRIDGE = 168
    NOSE_BOTTOM = 2
    LEFT_ALAR = 98
    RIGHT_ALAR = 327

    # Bocca
    MOUTH_LEFT = 61
    MOUTH_RIGHT = 291
    MOUTH_TOP = 13
    MOUTH_BOTTOM = 14
    UPPER_LIP_TOP = 0
    LOWER_LIP_BOTTOM = 17

    # Mascella e mento
    CHIN = 152
    CHIN_LEFT = 140
    CHIN_RIGHT = 377
    JAW_LEFT = 234
    JAW_RIGHT = 454
    GONION_LEFT = 58
    GONION_RIGHT = 288

    # Zigomi
    LEFT_ZYGOMATIC = 50
    RIGHT_ZYGOMATIC = 280

    # Linea mediana
    MID_FOREHEAD = 10
    MID_NOSE_BRIDGE = 6
    MID_NOSE_TIP = 1

    # Orecchie (per larghezza totale)
    TRAGUS_LEFT = 234
    TRAGUS_RIGHT = 454


# ─── INIZIALIZZAZIONE MEDIAPIPE ───

mp_face_mesh = __import__('mediapipe').solutions.face_mesh

def create_face_mesh():
    """Crea un'istanza di Face Mesh con configurazione ottimale"""
    return mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,  # Include iris e labbra dettagliate
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )


# ─── ESTRAZIONE LANDMARK ───

def extract_landmarks(image: np.ndarray, face_mesh=None) -> Optional[FaceLandmarks]:
    """
    Estrae 478 landmark da una immagine.
    Ritorna None se non trova volti.
    """
    if face_mesh is None:
        face_mesh = create_face_mesh()

    h, w = image.shape[:2]
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return None

    landmarks = results.multi_face_landmarks[0]

    points_2d = []
    points_3d = []

    for lm in landmarks.landmark:
        points_2d.append([lm.x * w, lm.y * h])
        points_3d.append([lm.x, lm.y, lm.z])

    return FaceLandmarks(
        points_3d=np.array(points_3d),
        points_2d=np.array(points_2d),
        image_width=w,
        image_height=h,
        confidence=1.0  # MediaPipe non fornisce confidence per singolo landmark
    )


# ─── ANALISI SIMMETRIA ───

def calculate_symmetry(landmarks: FaceLandmarks) -> SymmetryMetrics:
    """
    Calcola metriche di simmetria confrontando lato sinistro e destro.
    La simmetria è la similitudine tra i landmark speculari.
    """
    pts = landmarks.points_3d
    li = LandmarkIndices

    # Coppie di landmark simmetrici da confrontare
    symmetric_pairs = [
        (li.LEFT_EYE_OUTER, li.RIGHT_EYE_OUTER),
        (li.LEFT_EYE_INNER, li.RIGHT_EYE_INNER),
        (li.LEFT_EYE_TOP, li.RIGHT_EYE_TOP),
        (li.LEFT_EYE_BOTTOM, li.RIGHT_EYE_BOTTOM),
        (li.LEFT_BROW_OUTER, li.RIGHT_BROW_OUTER),
        (li.LEFT_BROW_INNER, li.RIGHT_BROW_INNER),
        (li.LEFT_ALAR, li.RIGHT_ALAR),
        (li.MOUTH_LEFT, li.MOUTH_RIGHT),
        (li.JAW_LEFT, li.JAW_RIGHT),
        (li.CHIN_LEFT, li.CHIN_RIGHT),
        (li.LEFT_ZYGOMATIC, li.RIGHT_ZYGOMATIC),
        (li.GONION_LEFT, li.GONION_RIGHT),
    ]

    def mirror_point(point: np.ndarray) -> np.ndarray:
        """Specchia un punto attraverso l'asse mediano del viso"""
        mirrored = point.copy()
        mirrored[0] = 1.0 - mirrored[0]  # Specchia intorno a 0.5
        return mirrored

    # Raggruppa per feature
    eye_scores = []
    brow_scores = []
    nose_scores = []
    lip_scores = []
    jaw_scores = []

    for left_idx, right_idx in symmetric_pairs:
        left_pt = pts[left_idx]
        right_pt = pts[right_idx]
        # Distanza tra punto sinistro specchiato e punto destro reale
        mirrored_left = mirror_point(left_pt)
        distance = np.linalg.norm(mirrored_left - right_pt)

        # Normalizza per dimensione faccia (distanza inter-tragus)
        face_width = np.linalg.norm(pts[li.TRAGUS_LEFT] - pts[li.TRAGUS_RIGHT])
        if face_width == 0:
            face_width = 1.0
        normalized_distance = distance / face_width

        # Converti in score: 0 distanza = 100% simmetria
        score = max(0, 100 - normalized_distance * 500)

        if left_idx in [li.LEFT_EYE_OUTER, li.LEFT_EYE_INNER, li.LEFT_EYE_TOP, li.LEFT_EYE_BOTTOM]:
            eye_scores.append(score)
        elif left_idx in [li.LEFT_BROW_OUTER, li.LEFT_BROW_INNER]:
            brow_scores.append(score)
        elif left_idx in [li.LEFT_ALAR]:
            nose_scores.append(score)
        elif left_idx in [li.MOUTH_LEFT]:
            lip_scores.append(score)
        else:
            jaw_scores.append(score)

    # Deviazione linea mediana
    mid_forehead = pts[li.MID_FOREHEAD]
    mid_nose = pts[li.MID_NOSE_TIP]
    mid_chin = pts[li.CHIN]
    # Calcola quanto si discostano dal piano sagittale mediano
    midface_deviation = abs(mid_forehead[0]) + abs(mid_nose[0]) + abs(mid_chin[0])
    midface_mm = midface_deviation * 100  # Approssimazione mm, dipende da calibrazione

    overall = float(np.mean([
        np.mean(eye_scores) if eye_scores else 100,
        np.mean(brow_scores) if brow_scores else 100,
        np.mean(nose_scores) if nose_scores else 100,
        np.mean(lip_scores) if lip_scores else 100,
        np.mean(jaw_scores) if jaw_scores else 100,
    ]))

    return SymmetryMetrics(
        overall_symmetry=round(overall, 1),
        eye_symmetry=round(np.mean(eye_scores), 1) if eye_scores else 100.0,
        brow_symmetry=round(np.mean(brow_scores), 1) if brow_scores else 100.0,
        nose_symmetry=round(np.mean(nose_scores), 1) if nose_scores else 100.0,
        lip_symmetry=round(np.mean(lip_scores), 1) if lip_scores else 100.0,
        jaw_symmetry=round(np.mean(jaw_scores), 1) if jaw_scores else 100.0,
        midface_deviation_mm=round(midface_mm, 2),
    )


# ─── ANALISI PROPORZIONI ───

def calculate_proportions(landmarks: FaceLandmarks) -> ProportionMetrics:
    """Calcola le proporzioni facciali canoniche"""
    pts = landmarks.points_3d
    li = LandmarkIndices

    # Helper: distanza euclidea 3D
    def dist(i1, i2):
        return float(np.linalg.norm(pts[i1] - pts[i2]))

    # Altezza totale viso (attaccatura capelli stimata → mento)
    # Usiamo NOSE_BRIDGE (glabella) come proxy attaccatura
    forehead_top = pts[li.MID_FOREHEAD]
    chin = pts[li.CHIN]
    total_height = float(np.linalg.norm(forehead_top - chin))

    # Terzi facciali
    glabella = pts[li.NOSE_BRIDGE]
    nose_bottom = pts[li.NOSE_BOTTOM]

    upper_height = float(np.linalg.norm(forehead_top - glabella))
    middle_height = float(np.linalg.norm(glabella - nose_bottom))
    lower_height = float(np.linalg.norm(nose_bottom - chin))

    upper_ratio = upper_height / total_height if total_height > 0 else 0
    middle_ratio = middle_height / total_height if total_height > 0 else 0
    lower_ratio = lower_height / total_height if total_height > 0 else 0

    # Larghezze
    face_width = dist(li.TRAGUS_LEFT, li.TRAGUS_RIGHT)
    bizygomatic_width = dist(li.LEFT_ZYGOMATIC, li.RIGHT_ZYGOMATIC)
    bigonial_width = dist(li.GONION_LEFT, li.GONION_RIGHT)
    eye_distance = dist(li.LEFT_EYE_INNER, li.RIGHT_EYE_INNER)
    nose_width = dist(li.LEFT_ALAR, li.RIGHT_ALAR)
    mouth_width = dist(li.MOUTH_LEFT, li.MOUTH_RIGHT)

    # Indice facciale (altezza/larghezza)
    facial_idx = total_height / bizygomatic_width if bizygomatic_width > 0 else 0
    # Euriprosopo < 84, Mesoprosopo 84-89, Leptoprosopo > 89

    # Proiezione mento (quanto il mento sporge rispetto al piano facciale)
    chin_projection = pts[li.CHIN][2]  # componente z = profondità
    # Normalizziamo con la larghezza per avere un ratio
    chin_proj_ratio = abs(chin_projection) / face_width if face_width > 0 else 0

    # Angolo mandibolare (approssimato)
    # Tra GONION → CHIN → GONION_ALTRO_LATO
    gonion_left = pts[li.GONION_LEFT]
    chin_pt = pts[li.CHIN]
    gonion_right = pts[li.GONION_RIGHT]

    # Calcoliamo l'angolo al mento
    v1 = gonion_left - chin_pt
    v2 = gonion_right - chin_pt
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)
    cos_angle = np.clip(cos_angle, -1, 1)
    jaw_angle = float(np.degrees(np.arccos(cos_angle)))

    # Angolo goniale (approssimato da BIGONIAL / BIZYGOMATIC ratio)
    gonial = bigonial_width / bizygomatic_width if bizygomatic_width > 0 else 0

    return ProportionMetrics(
        upper_third_ratio=round(upper_ratio, 4),
        middle_third_ratio=round(middle_ratio, 4),
        lower_third_ratio=round(lower_ratio, 4),
        facial_index=round(facial_idx, 1),
        intercanthal_distance_ratio=round(eye_distance / face_width, 4) if face_width > 0 else 0,
        nasal_width_ratio=round(nose_width / face_width, 4) if face_width > 0 else 0,
        mouth_width_ratio=round(mouth_width / face_width, 4) if face_width > 0 else 0,
        chin_projection_ratio=round(chin_proj_ratio, 4),
        jaw_angle=round(jaw_angle, 1),
        gonial_angle=round(gonial, 4),
        bigonial_width_ratio=round(bigonial_width / bizygomatic_width, 4) if bizygomatic_width > 0 else 0,
    )


# ─── CANTHAL TILT ───

def calculate_canthal_tilt(landmarks: FaceLandmarks) -> Tuple[float, float]:
    """
    Calcola inclinazione rima palpebrale (canthal tilt).
    Positivo = occhi da gatto (attraente), Negativo = occhi cadenti.
    Ritorna (tilt_sinistro, tilt_destro) in gradi.
    """
    pts = landmarks.points_2d
    li = LandmarkIndices

    def tilt_angle(outer_idx, inner_idx):
        outer = pts[outer_idx]
        inner = pts[inner_idx]
        dx = outer[0] - inner[0]
        dy = outer[1] - inner[1]
        return float(np.degrees(np.arctan2(dy, dx)))

    left_tilt = tilt_angle(li.LEFT_EYE_OUTER, li.LEFT_EYE_INNER)
    right_tilt = tilt_angle(li.RIGHT_EYE_INNER, li.RIGHT_EYE_OUTER)  # invertito per specularità

    # Media: positivo = upturned (attraente), range tipico -15 a +15
    right_tilt_corrected = -right_tilt
    mean_tilt = (left_tilt + right_tilt_corrected) / 2

    return mean_tilt


# ─── CALCOLO MASCOLINITÀ/FEMMINILITÀ ───

def calculate_masculinity_femininity(landmarks: FaceLandmarks) -> float:
    """
    Stima approssimativa mascolinità/femminilità basata su rapporti craniofacciali.
    >50 = tratti più maschili, <50 = tratti più femminili.
    Basata su studi di antropometria di Farkas.
    """
    pts = landmarks.points_3d
    li = LandmarkIndices
    prop = calculate_proportions(landmarks)

    score = 50.0

    # Mascella più larga (bigoniale) = più maschile
    if prop.bigonial_width_ratio > 0.85:
        score += 10
    elif prop.bigonial_width_ratio < 0.75:
        score -= 10

    # Mento più prominente = più maschile
    if prop.chin_projection_ratio > 0.045:
        score += 8
    elif prop.chin_projection_ratio < 0.030:
        score -= 8

    # Sopracciglia più basse = più maschili
    brow_y = pts[li.LEFT_BROW_INNER][1]
    eye_y = pts[li.LEFT_EYE_TOP][1]
    brow_height = brow_y - eye_y
    if brow_height < 0.02:  # Sopracciglia basse
        score += 6
    elif brow_height > 0.05:  # Sopracciglia alte
        score -= 6

    # Labbra più sottili = più maschili
    lip_height = abs(pts[li.MOUTH_TOP][1] - pts[li.MOUTH_BOTTOM][1])
    face_h = abs(pts[li.MID_FOREHEAD][1] - pts[li.CHIN][1])
    lip_ratio = lip_height / face_h if face_h > 0 else 0.02
    if lip_ratio < 0.015:
        score += 5
    elif lip_ratio > 0.025:
        score -= 5

    return max(0, min(100, score))


# ─── ANALISI COMPLETA ───

def analyze_face(image: np.ndarray) -> Optional[FacialAnalysis]:
    """
    Esegue l'analisi facciale completa su una singola immagine.
    Ritorna None se non viene rilevato un volto.
    """
    face_mesh = create_face_mesh()
    landmarks = extract_landmarks(image, face_mesh)
    face_mesh.close()

    if landmarks is None:
        return None

    symmetry = calculate_symmetry(landmarks)
    proportions = calculate_proportions(landmarks)
    canthal = calculate_canthal_tilt(landmarks)
    masculinity = calculate_masculinity_femininity(landmarks)

    # Rapporti aurei (phi = 1.618)
    phi = 1.618
    golden_ratios = {
        "face_height_width": round(proportions.facial_index / phi, 3),
        "nose_width_mouth_width": round(
            (proportions.nasal_width_ratio / proportions.mouth_width_ratio) / phi, 3
        ) if proportions.mouth_width_ratio > 0 else 0,
        "upper_lower_third": round(
            (proportions.upper_third_ratio / proportions.lower_third_ratio), 3
        ) if proportions.lower_third_ratio > 0 else 0,
    }

    return FacialAnalysis(
        symmetry=symmetry,
        proportions=proportions,
        face_shape=_classify_face_shape(proportions),
        masculinity_femininity=round(masculinity, 1),
        canthal_tilt=round(canthal, 1),
        brow_position=0.0,  # TODO: calibrare
        perceived_golden_ratios=golden_ratios,
        raw_landmarks=[landmarks],
    )


def _classify_face_shape(prop: ProportionMetrics) -> str:
    """Classifica la forma del viso in 7 tipi standard"""
    ratio = prop.facial_index
    jaw = prop.bigonial_width_ratio

    if ratio < 84:
        # Viso largo
        if jaw < 0.75:
            return "oval"
        elif jaw > 0.85:
            return "square"
        return "round"
    elif ratio > 89:
        # Viso lungo
        if jaw > 0.80:
            return "rectangle"
        return "oblong"
    else:
        if jaw > 0.82:
            return "triangle"
        return "heart" if jaw < 0.75 else "diamond"


# ─── ANALISI MULTI-FOTO ───

def analyze_multiple_photos(images: List[np.ndarray]) -> Dict:
    """
    Analizza 6 foto standardizzate e aggrega i risultati.
    Ordine atteso: frontale, profilo dx, profilo sx, 3/4 dx, 3/4 sx, frontale sorridente
    """
    analyses = []
    for img in images:
        result = analyze_face(img)
        if result:
            analyses.append(result)

    if not analyses:
        return {"error": "Nessun volto rilevato nelle foto"}

    # Aggrega
    primary = analyses[0]  # Foto frontale = riferimento

    # Media simmetria su tutte le foto frontali
    symmetries = [a.symmetry.overall_symmetry for a in analyses]
    avg_symmetry = np.mean(symmetries)

    return {
        "symmetry": primary.symmetry.__dict__ if primary else {},
        "proportions": primary.proportions.__dict__ if primary else {},
        "face_shape": primary.face_shape,
        "masculinity_femininity": primary.masculinity_femininity,
        "canthal_tilt": primary.canthal_tilt,
        "golden_ratios": primary.perceived_golden_ratios,
        "num_faces_detected": len(analyses),
        "confidence": min(len(analyses) / 6, 1.0),
    }
