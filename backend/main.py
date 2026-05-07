"""MORPHIC — Backend API. Analisi facciale AI senza database esterno."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import time

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("eidos_api_starting")
    yield
    logger.info("eidos_api_shutdown")


app = FastAPI(
    title="MORPHIC API",
    description="AI-powered facial aesthetics analysis",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    logger.info("http", method=request.method, path=request.url.path, status=response.status_code, ms=round((time.time() - start) * 1000, 1))
    return response


@app.exception_handler(Exception)
async def global_exception(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": str(exc)})


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/")
async def root():
    return {"name": "MORPHIC API", "docs": "/docs"}


# Routes — with safe imports if AI deps missing on Railway
try:
    from api.routes.analysis import router as analysis_router
    app.include_router(analysis_router)
except ImportError as e:
    @app.get("/api/v1/analyze")
    async def analyze_unavailable():
        return {"error": "AI engine initializing. Please try again in a few minutes.", "detail": str(e)[:100]}

    @app.get("/api/v1/analysis/{analysis_id}")
    async def analysis_unavailable(analysis_id: str):
        return {"error": "AI engine initializing", "status": "unavailable"}
