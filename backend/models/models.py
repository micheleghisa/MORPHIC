"""
GLOWUP AI — Database Models (SQLAlchemy)
Tabelle: users, analyses, reports, social_content
"""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    DateTime, Text, JSON, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import DeclarativeBase, relationship
import enum
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


# ─── ENUMS ───

class AnalysisStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"           # 1 analisi/mese
    UNLIMITED = "unlimited"

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class SkinType(str, enum.Enum):
    DRY = "dry"
    OILY = "oily"
    COMBINATION = "combination"
    NORMAL = "normal"
    SENSITIVE = "sensitive"

class FitzpatrickScale(str, enum.Enum):
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"
    V = "V"
    VI = "VI"


# ─── MODELS ───

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True, unique=True)
    subscription_tier = Column(
        SAEnum(SubscriptionTier),
        default=SubscriptionTier.FREE,
        nullable=False
    )
    subscription_active = Column(Boolean, default=False)
    analyses_this_month = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    gdpr_consent = Column(Boolean, default=False)
    data_deletion_requested = Column(Boolean, default=False)

    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")

    def can_analyse(self) -> bool:
        if self.subscription_tier == SubscriptionTier.UNLIMITED:
            return True
        if self.subscription_tier == SubscriptionTier.PRO:
            return self.analyses_this_month < 1
        return self.analyses_this_month < 1  # free tier: 1 gratuita totale


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(
        SAEnum(AnalysisStatus),
        default=AnalysisStatus.QUEUED,
        nullable=False
    )

    # Metadati utente (self-reported)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    ethnicity = Column(String(100), nullable=True)
    skin_type = Column(String(30), nullable=True)
    skin_concerns = Column(JSON, nullable=True)  # ["acne", "wrinkles", "pigmentation"]
    goals = Column(JSON, nullable=True)  # ["symmetry", "skin_quality", "jawline"]
    lifestyle_factors = Column(JSON, nullable=True)

    # Foto
    photo_urls = Column(JSON, nullable=True)  # [URL front, URL profile_left, ...]

    # Risultati analisi AI
    landmarks_data = Column(JSON, nullable=True)       # 478 punti MediaPipe x 6 foto
    symmetry_score = Column(Float, nullable=True)       # 0-100
    proportion_scores = Column(JSON, nullable=True)     # Dizionario proporzioni facciali
    skin_analysis = Column(JSON, nullable=True)         # Texture, pigmentazione, rughe
    biometric_scores = Column(JSON, nullable=True)      # Tutti gli score aggregati
    perceived_age = Column(Integer, nullable=True)
    perceived_gender = Column(String(20), nullable=True)
    perceived_ethnicity = Column(String(100), nullable=True)
    face_shape = Column(String(50), nullable=True)
    masculinity_femininity_score = Column(Float, nullable=True)

    # Report generato
    report_text = Column(Text, nullable=True)           # Markdown report
    report_json = Column(JSON, nullable=True)           # Structured data
    protocol = Column(JSON, nullable=True)              # Raccomandazioni
    before_after_images = Column(JSON, nullable=True)   # URL visualizzazioni

    # Metadati
    processing_time_seconds = Column(Float, nullable=True)
    llm_provider_used = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)     # 0-1, quanto l'AI è sicura
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="analyses")


class Recommendation(Base):
    """Catalogo raccomandazioni evidence-based (usato nei prompt)"""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100), nullable=True)
    concern = Column(String(200), nullable=False)
    recommendation_text = Column(Text, nullable=False)
    evidence_level = Column(String(20), default="moderate")  # strong, moderate, weak
    budget_option = Column(Text, nullable=True)
    premium_option = Column(Text, nullable=True)
    free_option = Column(Text, nullable=True)
    contraindications = Column(Text, nullable=True)
    applicable_gender = Column(String(20), default="all")
    min_age = Column(Integer, default=0)
    max_age = Column(Integer, default=100)
    tags = Column(JSON, nullable=True)


class SocialContent(Base):
    """Contenuti social generati automaticamente"""
    __tablename__ = "social_content"

    id = Column(String, primary_key=True, default=generate_uuid)
    platform = Column(String(50), nullable=False)       # tiktok, instagram, youtube
    content_type = Column(String(50), nullable=False)   # video, image, carousel
    script = Column(Text, nullable=True)
    hashtags = Column(JSON, nullable=True)
    media_url = Column(String(500), nullable=True)
    status = Column(String(50), default="draft")        # draft, scheduled, published
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    meta_ad_id = Column(String(255), nullable=True)
    performance_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
