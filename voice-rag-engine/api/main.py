"""FastAPI backend for production voice-RAG requests."""

from __future__ import annotations

import asyncio
import base64
import inspect
import logging
from pathlib import Path
import re
import shutil
import tempfile
import time
from typing import Any
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import os
from api.config import APISettings, load_api_settings
from rag.pipeline import TextRAGPipeline
from voice.stt.sarvam import SarvamSTT
from voice.stt.mock import MockSTT
from voice.tts.sarvam import SarvamTTS
from voice.tts.mock import MockTTS
from voice.voice_rag import VoiceRAG


logger = logging.getLogger("voice_rag.api")

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")

ERROR_STATUS_BY_TYPE = {
    "InvalidAudioError": 400,
    "EmptyUploadError": 400,
    "EmptyTranscriptError": 422,
    "STTError": 502,
    "RAGError": 502,
    "LLMError": 502,
    "TimeoutError": 504,
}


def create_app() -> FastAPI:
    app = FastAPI(
        title="Voice RAG Engine API",
        version="0.1.0",
        description="Production API for audio upload, STT, RAG answering, and optional TTS synthesis.",
    )
    app.state.api_settings = load_api_settings()
    app.state.voice_rag = None
    configure_cors(app, app.state.api_settings)
    app.include_router(create_routes())
    register_exception_handlers(app)
    return app


def configure_cors(app: FastAPI, settings: APISettings) -> None:
    origins = list(settings.allowed_cors_origins)
    for origin in ("https://voice-rag-engine.vercel.app", "http://localhost:8080", "http://127.0.0.1:8080"):
        if origin not in origins:
            origins.append(origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if "*" in origins else origins,
        allow_origin_regex=r"https://.*\.vercel\.app" if "*" not in origins else None,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )


def create_routes():
    from fastapi import APIRouter

    router = APIRouter()

    @router.get("/", summary="Root endpoint")
    def root(request: Request, response: Response) -> dict:
        """Return status and links to health check, docs, and web UI."""
        request_id = get_request_id(request)
        response.headers["X-Request-ID"] = request_id
        settings = get_settings(request)
        return {
            "status": "ok",
            "service": settings.app_name,
            "version": settings.app_version,
            "request_id": request_id,
            "web_ui": "http://localhost:8080/",
            "health": "/health",
            "docs": "/docs",
        }

    @router.get("/health", summary="Service health")
    def health(request: Request, response: Response) -> dict:
        """Return lightweight service health without calling external providers."""
        request_id = get_request_id(request)
        response.headers["X-Request-ID"] = request_id
        settings = get_settings(request)
        return {
            "status": "ok",
            "service": settings.app_name,
            "version": settings.app_version,
            "request_id": request_id,
        }

    @router.post("/voice/query", summary="Answer a voice query")
    async def voice_query(
        request: Request,
        response: Response,
        audio: UploadFile = File(..., description="Audio file to transcribe and answer."),
        language: str = Form(None, description="Selected language code (e.g. 'hi', 'en', 'bn', etc.)"),
        voice_rag: VoiceRAG = Depends(get_voice_rag),
    ) -> dict:
        """Process an uploaded audio file through the existing VoiceRAG pipeline."""
        request_id = get_request_id(request)
        response.headers["X-Request-ID"] = request_id
        settings = get_settings(request)
        start = time.time()

        logger.info(
            "voice_query_start",
            extra={
                "request_id": request_id,
                "filename": safe_filename(audio.filename),
                "content_type": audio.content_type,
                "language": language,
            },
        )

        temp_path: Path | None = None
        try:
            temp_path = await persist_upload_to_temp(audio, settings)
            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(call_process_audio, voice_rag, str(temp_path), language),
                    timeout=settings.request_timeout_seconds,
                )
            except asyncio.TimeoutError:
                raise_api_error(
                    status_code=504,
                    error_type="TimeoutError",
                    message="Voice query timed out.",
                    request_id=request_id,
                )

            payload = build_voice_response(result, request_id)
            status_code = status_for_voice_result(result)
            log_voice_result(request_id, payload, status_code, start)

            if status_code >= 400:
                return JSONResponse(status_code=status_code, content=payload, headers={"X-Request-ID": request_id})
            return payload
        except HTTPException:
            raise
        except Exception:
            logger.exception("voice_query_unexpected_error", extra={"request_id": request_id})
            raise_api_error(
                status_code=500,
                error_type="InternalServerError",
                message="Unexpected internal error while processing voice query.",
                request_id=request_id,
            )
        finally:
            await close_upload(audio)
            cleanup_temp_path(temp_path)

    return router


def call_process_audio(voice_rag: VoiceRAG, audio_path: str, language: str | None) -> dict:
    """Call real VoiceRAG and older test doubles without assuming signature parity."""
    signature = inspect.signature(voice_rag.process_audio)
    parameters = signature.parameters
    accepts_language = (
        "language" in parameters
        or any(param.kind == inspect.Parameter.VAR_KEYWORD for param in parameters.values())
        or any(param.kind == inspect.Parameter.VAR_POSITIONAL for param in parameters.values())
    )
    if accepts_language:
        return voice_rag.process_audio(audio_path, language=language)
    return voice_rag.process_audio(audio_path)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = get_request_id(request)
        return JSONResponse(
            status_code=422,
            content={
                "request_id": request_id,
                "error": {
                    "type": "ValidationError",
                    "message": "Malformed request.",
                    "details": exc.errors(),
                },
            },
            headers={"X-Request-ID": request_id},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        request_id = get_request_id(request)
        detail = exc.detail if isinstance(exc.detail, dict) else {}
        error = detail.get("error") or {
            "type": "HTTPError",
            "message": str(exc.detail),
        }
        return JSONResponse(
            status_code=exc.status_code,
            content={"request_id": detail.get("request_id", request_id), "error": error},
            headers={"X-Request-ID": detail.get("request_id", request_id)},
        )


def get_settings(request: Request) -> APISettings:
    return request.app.state.api_settings


def get_voice_rag(request: Request) -> VoiceRAG:
    if request.app.state.voice_rag is None:
        request.app.state.voice_rag = build_voice_rag(get_settings(request))
    return request.app.state.voice_rag


def build_voice_rag(settings: APISettings) -> VoiceRAG:
    sarvam_key = os.getenv("SARVAM_API_KEY", "").strip()
    if sarvam_key and not sarvam_key.startswith("your_"):
        try:
            stt = SarvamSTT(timeout=settings.stt_timeout_seconds)
        except Exception:
            stt = MockSTT()
    else:
        stt = MockSTT()

    if settings.enable_tts:
        if sarvam_key and not sarvam_key.startswith("your_"):
            try:
                tts = SarvamTTS(timeout=settings.tts_timeout_seconds)
            except Exception:
                tts = MockTTS()
        else:
            tts = MockTTS()
    else:
        tts = None

    rag_pipeline = TextRAGPipeline(
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
        llm_timeout_seconds=settings.llm_timeout_seconds,
    )
    return VoiceRAG(stt=stt, rag_pipeline=rag_pipeline, tts=tts)


def get_request_id(request: Request) -> str:
    value = request.headers.get("X-Request-ID")
    if value:
        candidate = value.strip()
        if REQUEST_ID_PATTERN.fullmatch(candidate):
            request.state.request_id = candidate
            return candidate
    existing = getattr(request.state, "request_id", None)
    if existing:
        return existing
    request.state.request_id = str(uuid4())
    return request.state.request_id


def validate_upload_metadata(audio: UploadFile, settings: APISettings) -> str:
    filename = audio.filename or ""
    suffix = Path(filename).suffix.lower()
    content_type = (audio.content_type or "").split(";")[0].strip().lower()

    if not filename or suffix not in settings.supported_extensions:
        raise_api_error(415, "InvalidAudioError", "Unsupported audio file extension.")
    if content_type not in settings.supported_mime_types:
        raise_api_error(415, "InvalidAudioError", "Unsupported audio content type.")
    return suffix


async def persist_upload_to_temp(audio: UploadFile, settings: APISettings) -> Path:
    suffix = validate_upload_metadata(audio, settings)
    temp_dir = Path(tempfile.mkdtemp(prefix="voice-rag-", dir=settings.temp_dir))
    temp_path = temp_dir / f"upload{suffix}"
    total = 0

    try:
        with temp_path.open("wb") as handle:
            while True:
                chunk = await audio.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > settings.max_upload_bytes:
                    raise_api_error(413, "InvalidAudioError", "Uploaded audio exceeds the configured size limit.")
                handle.write(chunk)
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise

    if total == 0:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise_api_error(400, "EmptyUploadError", "Uploaded audio is empty.")
    return temp_path


def cleanup_temp_path(path: Path | None) -> None:
    if path is None:
        return
    shutil.rmtree(path.parent, ignore_errors=True)


async def close_upload(audio: UploadFile) -> None:
    try:
        await audio.close()
    except Exception:
        logger.warning("upload_close_failed")


def build_voice_response(result: dict[str, Any], request_id: str) -> dict[str, Any]:
    payload = dict(result)
    sanitize_error_payload(payload)
    payload.setdefault("transcription", payload.get("transcript", ""))
    payload.setdefault("refusal", payload.get("refused", False))
    payload.setdefault("language", payload.get("normalized_language") or payload.get("language_code"))
    if not payload.get("sources"):
        payload["sources"] = build_source_items(payload.get("retrieved_passages", []))
    audio = payload.pop("tts_audio", None)
    if isinstance(audio, bytes):
        payload["tts_audio_base64"] = base64.b64encode(audio).decode("ascii")
        payload["tts_audio_bytes"] = len(audio)
    else:
        payload["tts_audio_base64"] = None
        payload["tts_audio_bytes"] = 0
    payload["request_id"] = request_id
    return payload


def build_source_items(retrieved_passages: Any) -> list[dict[str, Any]]:
    if not isinstance(retrieved_passages, list):
        return []
    sources = []
    for idx, meta in enumerate(retrieved_passages):
        if not isinstance(meta, dict):
            continue
        query_id = meta.get("query_id", "unknown")
        passage_index = meta.get("passage_index", idx)
        chunk_index = meta.get("chunk_index", 0)
        sources.append(
            {
                "id": f"{query_id}_{passage_index}_{chunk_index}",
                "title": f"Source {idx + 1}",
                "reference": str(meta.get("dataset") or meta.get("record_id") or query_id),
                "snippet": meta.get("text", ""),
            }
        )
    return sources


def sanitize_error_payload(payload: dict[str, Any]) -> None:
    error = payload.get("error")
    if not isinstance(error, dict):
        return
    message = error.get("message")
    if not isinstance(message, str):
        return
    message = re.sub(r"[A-Za-z]:\\[^\s]+", "[path]", message)
    message = re.sub(r"/(?:tmp|var|home|Users)/[^\s]+", "[path]", message)
    error["message"] = message


def status_for_voice_result(result: dict[str, Any]) -> int:
    error = result.get("error") if isinstance(result, dict) else None
    if not error:
        return 200
    error_type = error.get("type", "InternalServerError")
    return ERROR_STATUS_BY_TYPE.get(error_type, 500)


def log_voice_result(request_id: str, payload: dict[str, Any], status_code: int, start: float) -> None:
    logger.info(
        "voice_query_end",
        extra={
            "request_id": request_id,
            "status_code": status_code,
            "stt_provider": payload.get("stt_provider"),
            "stt_model": payload.get("stt_model"),
            "tts_provider": payload.get("tts_provider"),
            "tts_model": payload.get("tts_model"),
            "grounded": payload.get("grounded"),
            "refused": payload.get("refused"),
            "stt_latency_ms": payload.get("stt_latency_ms"),
            "rag_latency_ms": payload.get("rag_latency_ms"),
            "tts_latency_ms": payload.get("tts_latency_ms"),
            "total_latency_ms": payload.get("total_latency_ms"),
            "api_wall_latency_ms": (time.time() - start) * 1000.0,
            "success": status_code < 400,
            "error_type": (payload.get("error") or {}).get("type"),
        },
    )


def raise_api_error(status_code: int, error_type: str, message: str, request_id: str | None = None) -> None:
    detail = {
        "error": {
            "type": error_type,
            "message": message,
        }
    }
    if request_id:
        detail["request_id"] = request_id
    raise HTTPException(status_code=status_code, detail=detail)


def safe_filename(filename: str | None) -> str | None:
    if not filename:
        return None
    return Path(filename).name[:255]


app = create_app()
