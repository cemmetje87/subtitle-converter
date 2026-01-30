"""FastAPI application for subtitle search, download, and translation"""

import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .opensubtitles import OpenSubtitlesClient
from .translator import TranslatorClient
from .srt_utils import sync_subtitles, shift_subtitles, time_string_to_ms

# Load environment variables
load_dotenv()

# Config
OPENSUBTITLES_API_KEY = os.getenv("OPENSUBTITLES_API_KEY", "")
LIBRETRANSLATE_URL = os.getenv("LIBRETRANSLATE_URL", "http://localhost:5000")
LIBRETRANSLATE_API_KEY = os.getenv("LIBRETRANSLATE_API_KEY", "")

# Clients (initialized on startup)
opensubtitles_client: Optional[OpenSubtitlesClient] = None
translator_client: Optional[TranslatorClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize clients on startup"""
    global opensubtitles_client, translator_client

    if not OPENSUBTITLES_API_KEY:
        print("WARNING: OPENSUBTITLES_API_KEY not set. API calls will fail.")

    opensubtitles_client = OpenSubtitlesClient(OPENSUBTITLES_API_KEY)
    translator_client = TranslatorClient(
        base_url=LIBRETRANSLATE_URL,
        api_key=LIBRETRANSLATE_API_KEY if LIBRETRANSLATE_API_KEY else None
    )

    yield  # App runs here

    # Cleanup
    opensubtitles_client = None
    translator_client = None


app = FastAPI(
    title="Subtitle Converter",
    description="Search, download, and translate subtitles from OpenSubtitles.org",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class DownloadRequest(BaseModel):
    file_id: int
    filename: Optional[str] = "subtitle.srt"
    sync_time: Optional[str] = None  # Optional: sync first subtitle to this time


class TranslateRequest(BaseModel):
    file_id: int
    source_lang: str = "en"
    target_lang: str = "th"
    filename: Optional[str] = "subtitle_translated.srt"
    sync_time: Optional[str] = None  # Optional: sync first subtitle to this time


class SyncRequest(BaseModel):
    file_id: int
    sync_time: str  # Time for first subtitle (e.g., "00:01:23,456" or "83.456" seconds)
    filename: Optional[str] = "subtitle_synced.srt"


# API Routes
@app.get("/api/languages")
async def get_opensubtitles_languages():
    """Get available subtitle languages from OpenSubtitles"""
    if not opensubtitles_client:
        raise HTTPException(status_code=500, detail="OpenSubtitles client not initialized")

    try:
        languages = await opensubtitles_client.get_languages()
        return {"languages": languages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/translation-languages")
async def get_translation_languages():
    """Get available translation languages from LibreTranslate"""
    if not translator_client:
        raise HTTPException(status_code=500, detail="Translator client not initialized")

    try:
        languages = await translator_client.get_languages()
        return {"languages": languages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search")
async def search_subtitles(
    query: str = Query(..., description="Movie or show name"),
    languages: str = Query("en", description="Comma-separated language codes"),
    imdb_id: Optional[str] = Query(None, description="IMDB ID"),
    year: Optional[int] = Query(None, description="Release year"),
    season: Optional[int] = Query(None, description="Season number"),
    episode: Optional[int] = Query(None, description="Episode number"),
):
    """Search for subtitles on OpenSubtitles.org"""
    if not opensubtitles_client:
        raise HTTPException(status_code=500, detail="OpenSubtitles client not initialized")

    try:
        results = await opensubtitles_client.search_subtitles(
            query=query,
            languages=languages,
            imdb_id=imdb_id,
            year=year,
            season_number=season,
            episode_number=episode,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/download")
async def download_subtitle(request: DownloadRequest):
    """Download a subtitle file, optionally synced to a start time"""
    if not opensubtitles_client:
        raise HTTPException(status_code=500, detail="OpenSubtitles client not initialized")

    try:
        content = await opensubtitles_client.download_subtitle(request.file_id)

        # Apply sync if specified
        if request.sync_time:
            try:
                sync_time_ms = time_string_to_ms(request.sync_time)
                content = sync_subtitles(content, sync_time_ms)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid sync time: {e}")

        return PlainTextResponse(
            content=content,
            media_type="text/plain",
            headers={
                "Content-Disposition": f'attachment; filename="{request.filename}"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sync")
async def sync_subtitle(request: SyncRequest):
    """Download and sync subtitle timing to start at specified time"""
    if not opensubtitles_client:
        raise HTTPException(status_code=500, detail="OpenSubtitles client not initialized")

    try:
        content = await opensubtitles_client.download_subtitle(request.file_id)

        # Parse the sync time and apply
        try:
            sync_time_ms = time_string_to_ms(request.sync_time)
            synced_content = sync_subtitles(content, sync_time_ms)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid sync time format: {e}")

        return PlainTextResponse(
            content=synced_content,
            media_type="text/plain",
            headers={
                "Content-Disposition": f'attachment; filename="{request.filename}"'
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/translate")
async def translate_subtitle(request: TranslateRequest):
    """Download and translate a subtitle file"""
    if not opensubtitles_client:
        raise HTTPException(status_code=500, detail="OpenSubtitles client not initialized")
    if not translator_client:
        raise HTTPException(status_code=500, detail="Translator client not initialized")

    try:
        # Download original subtitle
        content = await opensubtitles_client.download_subtitle(request.file_id)

        # Apply sync if specified (before translation)
        if request.sync_time:
            try:
                sync_time_ms = time_string_to_ms(request.sync_time)
                content = sync_subtitles(content, sync_time_ms)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid sync time: {e}")

        # Translate content
        translated = await translator_client.translate_subtitle_content(
            srt_content=content,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )

        return PlainTextResponse(
            content=translated,
            media_type="text/plain",
            headers={
                "Content-Disposition": f'attachment; filename="{request.filename}"'
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve static files (frontend)
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def serve_frontend():
    """Serve the main frontend page"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Subtitle Converter API", "docs": "/docs"}
