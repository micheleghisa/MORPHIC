"""
GLOWUP AI — Report Generator
Genera report estetico personalizzato usando LLM provider.
Usa SOLO dati numerici anonimizzati (GDPR-safe).
"""
import json
from typing import Dict, Any, List
import structlog

from services.llm_provider import get_llm_provider

logger = structlog.get_logger()


# ─── PROMPT TEMPLATE ───

SYSTEM_PROMPT = """You are a professional facial aesthetics analyst with 20+ years of experience in clinical facial analysis, dermatology, and cosmetic science. You write detailed, science-backed aesthetic reports for clients who want to improve their appearance without surgery.

Your tone: professional, warm, encouraging, and evidence-based. Never use flattery. Be honest but constructive. Every claim must reference anatomical facts or scientific studies.

IMPORTANT RULES:
1. You receive ONLY anonymized biometric data. No names, no photos.
2. Base all recommendations on the biometric data provided.
3. Include scores and measurements as provided.
4. Recommendations must be NON-SURGICAL only.
5. For each issue, suggest: one budget option, one premium option, one free option.
6. Format output in clear, structured Markdown.
7. NEVER recommend surgery, fillers, or invasive procedures unless clearly stated as non-surgical injectables option.
8. End with a personalized protocol (step-by-step plan).
9. Always include a disclaimer that recommendations should be verified with a healthcare professional.

REPORT STRUCTURE:
1. Executive Summary (3-4 sentence overview)
2. Facial Harmony & Symmetry Analysis
3. Facial Proportions & Structure
4. Skin Health Analysis
5. Feature-by-Feature Breakdown (eyes, nose, lips, jawline, etc.)
6. Biometric Scores Summary
7. Personalized Glow-Up Protocol (categories: skincare, hair, makeup, lifestyle, exercises, supplements, at-home devices, in-clinic treatments, dental, facial expressions)
8. Timeline & Expectations
9. Disclaimer"""


def build_user_prompt(
    age: int,
    gender: str,
    ethnicity: str,
    skin_type: str,
    skin_concerns: List[str],
    goals: List[str],
    biometric_data: Dict[str, Any],
    skin_data: Dict[str, Any],
) -> str:
    """Costruisce il prompt utente con SOLO dati numerici anonimizzati."""

    concerns_str = ", ".join(skin_concerns) if skin_concerns else "none specified"
    goals_str = ", ".join(goals) if goals else "general improvement"

    metrics = json.dumps(biometric_data, indent=2)
    skin = json.dumps(skin_data, indent=2)

    return f"""ANONYMIZED CLIENT PROFILE:

Demographics: {age} years old, {gender}, {ethnicity} ethnicity
Self-reported skin type: {skin_type}
Self-reported concerns: {concerns_str}
Client goals: {goals_str}

BIOMETRIC FACIAL ANALYSIS DATA:
{metrics}

SKIN ANALYSIS DATA:
{skin}

Based on the above biometric data, generate a complete facial aesthetics report following the structure provided in the system prompt. Be specific, reference the actual measurements, and provide actionable non-surgical recommendations tailored to this exact face.

Remember: the client CANNOT see their own face objectively. Your job is to give them clarity, confidence, and a clear path forward."""


# ─── REPORT GENERATOR ───

class ReportGenerator:
    """Genera report estetici personalizzati via LLM."""

    def __init__(self):
        self.llm = get_llm_provider()

    async def generate_report(
        self,
        age: int,
        gender: str,
        ethnicity: str,
        skin_type: str,
        skin_concerns: List[str],
        goals: List[str],
        biometric_data: Dict[str, Any],
        skin_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Genera un report estetico completo.
        Ritorna {"report_markdown": ..., "report_json": ..., "provider": ..., "latency_ms": ...}
        """
        user_prompt = build_user_prompt(
            age, gender, ethnicity, skin_type,
            skin_concerns, goals,
            biometric_data, skin_data
        )

        logger.info("generating_report", age=age, gender=gender)

        result = await self.llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=4000,
        )

        # Tenta di estrarre JSON strutturato dal Markdown
        # (l'LLM può restituire solo Markdown, va bene)
        report_md = result["content"]

        # Costruisci JSON strutturabile
        report_json = {
            "metadata": {
                "generated_by": "glowup-ai",
                "llm_provider": result["provider"],
                "age": age,
                "gender": gender,
                "ethnicity": ethnicity,
            },
            "biometrics": biometric_data,
            "skin_analysis": skin_data,
            "markdown_report": report_md,
        }

        return {
            "report_markdown": report_md,
            "report_json": report_json,
            "provider": result["provider"],
            "latency_ms": result["latency_ms"],
        }

    async def generate_social_content(
        self,
        topic: str,
        platform: str,
        tone: str = "educational",
        max_length: int = 500,
    ) -> Dict[str, Any]:
        """
        Genera contenuti per social media (TikTok, Instagram, YouTube).
        """
        social_prompt = f"""You are a social media content creator specializing in science-based facial aesthetics and beauty education.

Create content for {platform} about: {topic}

Requirements:
- Platform: {platform}
- Tone: {tone}
- Max length: {max_length} characters
- Include 5-8 relevant hashtags
- Add hook in first line
- End with call-to-action

Format:
```
HOOK: [first line]
BODY: [content]
CTA: [call to action]
HASHTAGS: [hashtags]
```"""

        result = await self.llm.generate(
            system_prompt="You are a viral content strategist for beauty and science channels.",
            user_prompt=social_prompt,
            temperature=0.7,
            max_tokens=800,
        )

        return {
            "content": result["content"],
            "provider": result["provider"],
            "platform": platform,
        }

    async def generate_ad_copy(
        self,
        target_audience: str,
        value_proposition: str,
    ) -> Dict[str, Any]:
        """
        Genera copy per Meta Ads.
        """
        ad_prompt = f"""Write 3 versions of Meta (Facebook/Instagram) ad copy for:

Product: AI-powered facial beauty analysis
Target audience: {target_audience}
Key value proposition: {value_proposition}

For each version provide:
1. Primary text (body of ad)
2. Headline (max 40 chars)
3. Description (max 30 chars)
4. Call to action button

Focus on curiosity and problem-solving. No hype, no false promises."""

        result = await self.llm.generate(
            system_prompt="You are a direct response copywriter for beauty-tech products. Write clear, compliant ad copy.",
            user_prompt=ad_prompt,
            temperature=0.6,
            max_tokens=1000,
        )

        return {
            "ad_copy": result["content"],
            "provider": result["provider"],
        }

    async def generate_chat_response(
        self,
        user_question: str,
        report_context: Dict[str, Any],
        chat_history: List[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Genera risposte per la chat assistente estetico AI.
        """
        messages = [{
            "role": "system",
            "content": f"""You are a friendly, knowledgeable aesthetic advisor for GlowUp AI.

You have access to the user's facial analysis report. Answer their questions about the report, their recommendations, or general beauty/aesthetics questions.

Report context (anonymized): {json.dumps(report_context, indent=2)}

Rules:
- Be supportive and encouraging. Never make the user feel bad.
- Base answers on the report data if relevant.
- For medical questions, always advise consulting a doctor.
- Keep responses under 200 words unless detail is needed.
- Suggest specific, actionable steps."""
        }]

        if chat_history:
            messages.extend(chat_history)

        messages.append({"role": "user", "content": user_question})

        # Usa chiamata diretta per la chat (non il template standard)
        result = await self.llm.generate(
            system_prompt=messages[0]["content"],
            user_prompt=user_question,
            temperature=0.5,
            max_tokens=500,
        )

        return {
            "response": result["content"],
            "provider": result["provider"],
        }


# ─── ISTANZA ───

_generator: ReportGenerator = None


def get_report_generator() -> ReportGenerator:
    global _generator
    if _generator is None:
        _generator = ReportGenerator()
    return _generator
