"""
MORPHIC — AI Before/After Visualization (Fal.ai Flux)
Genera una versione "glow-up" del viso preservando l'identità.
Usa Flux Pro su Fal.ai — qualità 7.5/10 vs QOVES.
"""
import os, base64, io
from typing import Dict, Optional
import numpy as np
import cv2
from PIL import Image
import fal_client
from config import settings


def image_to_base64_url(image: np.ndarray) -> str:
    """Converte immagine OpenCV in data URL base64."""
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"


async def generate_glowup_fal(
    image: np.ndarray,
    gender: str = "male",
    age: int = 25,
    skin_issues: list = None,
    proportion_issues: list = None,
) -> Optional[np.ndarray]:
    """
    Genera una versione migliorata del viso tramite Fal.ai Flux.
    Preserva l'identità ma applica i miglioramenti del protocollo glow-up.
    """
    if not settings.fal_key:
        print("⚠️  FAL_KEY not set")
        return None

    os.environ["FAL_KEY"] = settings.fal_key

    # Costruisci il prompt basato sui problemi rilevati
    improvements = []

    if skin_issues:
        if any("pigment" in str(s).lower() or "tone" in str(s).lower() for s in skin_issues):
            improvements.append("even skin tone, no hyperpigmentation")
        if any("acne" in str(s).lower() or "blemish" in str(s).lower() for s in skin_issues):
            improvements.append("clear skin, no acne, smooth texture")
        if any("wrinkle" in str(s).lower() or "aging" in str(s).lower() for s in skin_issues):
            improvements.append("youthful skin, reduced fine lines")
        if any("dark" in str(s).lower() or "circle" in str(s).lower() for s in skin_issues):
            improvements.append("bright under-eye area, no dark circles")

    if proportion_issues:
        if any("jaw" in str(p).lower() for p in proportion_issues):
            improvements.append("more defined jawline, sculpted chin")
        if any("symmetry" in str(p).lower() for p in proportion_issues):
            improvements.append("symmetrical facial features")
        if any("eye" in str(p).lower() or "brow" in str(p).lower() for p in proportion_issues):
            improvements.append("lifted eyebrows, brighter eyes")

    # Fallback: miglioramenti generici naturali
    if not improvements:
        improvements = [
            "clear smooth skin",
            "even skin tone",
            "bright alert eyes",
            "defined jawline",
            "well-groomed natural eyebrows",
            "healthy natural look",
        ]

    improv_text = ", ".join(improvements)

    # v1 prompt style — the one that worked
    if gender == "female":
        prompt = f"Same woman, identical facial identity and bone structure, but with: {improv_text}. Natural makeup, styled hair that frames the face well. Professional headshot, studio lighting, white background. VERY IMPORTANT: keep the exact same person. Just enhance naturally. No plastic surgery look. Photorealistic."
    else:
        prompt = f"Same man, identical facial identity and bone structure, but with: {improv_text}. Clean natural look, styled hair that suits the face shape. Professional headshot, studio lighting, white background. VERY IMPORTANT: keep the exact same person. Just enhance naturally. No plastic surgery look. Photorealistic."

    try:
        img_url = image_to_base64_url(image)
        print(f"   🎨 Fal.ai v1 generating...")

        result = fal_client.subscribe(
            "fal-ai/flux-pro/v1.1-ultra",
            arguments={
                "prompt": prompt,
                "image_url": img_url,
                "image_prompt_strength": 0.68,
                "num_images": 1,
                "safety_tolerance": "5",
            },
        )

        if result and "images" in result and len(result["images"]) > 0:
            import requests
            img_url_result = result["images"][0]["url"]
            resp = requests.get(img_url_result)
            result_img = Image.open(io.BytesIO(resp.content))
            result_rgb = np.array(result_img)

            # Preserve aspect ratio, center-crop to match original dimensions
            orig_h, orig_w = image.shape[:2]
            gen_h, gen_w = result_rgb.shape[:2]
            
            from PIL import Image as PILImage
            scale = orig_h / gen_h
            new_w = int(gen_w * scale)
            result_img_resized = result_img.resize((new_w, orig_h), PILImage.LANCZOS)
            result_arr = np.array(result_img_resized)
            
            if new_w >= orig_w:
                start_x = (new_w - orig_w) // 2
                result_cv = cv2.cvtColor(result_arr[:, start_x:start_x+orig_w, :], cv2.COLOR_RGB2BGR)
            else:
                canvas = PILImage.new("RGB", (orig_w, orig_h), (255, 255, 255))
                offset_x = (orig_w - new_w) // 2
                canvas.paste(result_img_resized, (offset_x, 0))
                result_cv = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)

            print(f"   ✅ Fal.ai v1 generated")
            return result_cv

        print(f"   ⚠️  Fal.ai unexpected result: {str(result)[:200]}")
        return None

    except Exception as e:
        print(f"   ⚠️  Fal.ai error: {str(e)[:200]}")
        return None


async def generate_before_after_composite(
    image: np.ndarray,
    gender: str = "male",
    age: int = 25,
    skin_concerns: list = None,
    goals: list = None,
) -> Dict[str, bytes]:
    """
    Genera il composite before/after usando Fal.ai + fallback morphing locale.
    Ritorna {"before_after": bytes, ...}
    """
    results = {}

    # STEP 1: AI Glow-Up via Fal.ai
    glowup = await generate_glowup_fal(image, gender, age, skin_concerns, goals)

    if glowup is not None:
        h, w = image.shape[:2]
        gh, gw = glowup.shape[:2]
        if gh != h:
            glowup = cv2.resize(glowup, (int(gw * h / gh), h))

        # Side-by-side composite
        composite = np.hstack([image, glowup])
        
        # Label bar
        font = cv2.FONT_HERSHEY_SIMPLEX
        bar_h = 42
        bar = np.ones((bar_h, composite.shape[1], 3), dtype=np.uint8) * 20
        cv2.putText(bar, "CURRENT", (18, 30), font, 0.55, (160, 160, 160), 1)
        cv2.putText(bar, "AFTER GLOW-UP", (w + 18, 30), font, 0.55, (120, 190, 255), 1)
        composite = np.vstack([bar, composite])

        _, buffer = cv2.imencode('.png', composite)
        results["full_glowup"] = buffer.tobytes()
        print("   ✅ Before/After composite ready")

    # STEP 2: Fallback — morphing geometrico locale
    from services.visualization import generate_all_visualizations
    from services.face_analysis import extract_landmarks

    landmarks = extract_landmarks(image)
    if landmarks:
        local_results = generate_all_visualizations(image, landmarks.points_2d)
        for key, img_bytes in local_results.items():
            if key not in results:
                results[key] = img_bytes

    return results
