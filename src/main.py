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

import rarfile
import logging

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
handlers = [logging.StreamHandler()]

# Only add file handler if LOG_FILE is set
log_file = os.getenv("LOG_FILE")
if log_file:
    handlers.append(logging.FileHandler(log_file))

logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

from .opensubtitles import OpenSubtitlesClient
from .subdl import SubDLClient
from .translator import TranslatorClient
from .srt_utils import sync_subtitles, shift_subtitles, time_string_to_ms
from .setup_unrar import setup_unrar

# Load environment variables
load_dotenv()

# Config
OPENSUBTITLES_API_KEY = os.getenv("OPENSUBTITLES_API_KEY", "")
SUBDL_API_KEY = os.getenv("SUBDL_API_KEY", "")
LIBRETRANSLATE_URL = os.getenv("LIBRETRANSLATE_URL", "http://localhost:5000")
LIBRETRANSLATE_API_KEY = os.getenv("LIBRETRANSLATE_API_KEY", "")

ARCHIVE_DIR = os.path.join(os.getcwd(), "archive")
CONVERTED_DIR = os.path.join(ARCHIVE_DIR, "converted")

# Clients (initialized on startup)
opensubtitles_client: Optional[OpenSubtitlesClient] = None
subdl_client: Optional[SubDLClient] = None
translator_client: Optional[TranslatorClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize clients and dependencies on startup"""
    global opensubtitles_client, subdl_client, translator_client

    # Setup directories
    os.makedirs(CONVERTED_DIR, exist_ok=True)
    print(f"INFO: Archive directories ensured at {ARCHIVE_DIR}")

    # Setup UnRAR
    try:
        unrar_path = setup_unrar()
        rarfile.UNRAR_TOOL = unrar_path
        print(f"INFO: UnRAR configured at {unrar_path}")
    except Exception as e:
        print(f"WARNING: Failed to setup UnRAR: {e}. RAR extraction will fail.")

    if not OPENSUBTITLES_API_KEY:
        print("WARNING: OPENSUBTITLES_API_KEY not set.")
    
    if not SUBDL_API_KEY:
         print("WARNING: SUBDL_API_KEY not set. SubDL calls will fail.")

    opensubtitles_client = OpenSubtitlesClient(OPENSUBTITLES_API_KEY)
    subdl_client = SubDLClient(SUBDL_API_KEY)
    
    translator_client = TranslatorClient(
        base_url=LIBRETRANSLATE_URL,
        api_key=LIBRETRANSLATE_API_KEY if LIBRETRANSLATE_API_KEY else None
    )

    yield  # App runs here

    # Cleanup
    opensubtitles_client = None
    subdl_client = None
    translator_client = None


app = FastAPI(
    title="Subtitle Converter",
    description="Search, download, and translate subtitles from SubDL & OpenSubtitles",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class DownloadRequest(BaseModel):
    file_id: str | int # Changed to allow string IDs for SubDL (urls)
    filename: Optional[str] = "subtitle.srt"
    sync_time: Optional[str] = None
    provider: Optional[str] = "subdl" # Default to subdl

class TranslateRequest(BaseModel):
    file_id: str | int
    source_lang: str = "en"
    target_lang: str = "th"
    filename: Optional[str] = "subtitle_translated.srt"
    sync_time: Optional[str] = None
    provider: Optional[str] = "subdl"

class SyncRequest(BaseModel):
    file_id: str | int
    sync_time: str
    filename: Optional[str] = "subtitle_synced.srt"
    provider: Optional[str] = "subdl"


# API Routes


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
    provider: str = Query("subdl", description="Provider: subdl or opensubtitles")
):
    """Search for subtitles"""
    try:
        if provider == "opensubtitles":
             if not opensubtitles_client:
                raise HTTPException(status_code=500, detail="OpenSubtitles client not initialized")
             results = await opensubtitles_client.search_subtitles(
                query=query, languages=languages, imdb_id=imdb_id, year=year,
                season_number=season, episode_number=episode
             )
             # Search results format differs, we might need to normalize if the frontend expects OS format.
             # My SubDL implementation attempts to normalize to {results: [...]}.
             return results
        
        else:
            # Default to SubDL
            if not subdl_client:
                 raise HTTPException(status_code=500, detail="SubDL client not initialized")
            
            # SubDL Search
            results = await subdl_client.search_subtitles(
                query=query, languages=languages, imdb_id=imdb_id, year=year,
                season_number=season, episode_number=episode
            )
            return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/download")
async def download_subtitle(request: DownloadRequest):
    """Download a subtitle file"""
    try:
        content = ""
        if request.provider == "opensubtitles":
             if not opensubtitles_client:
                  raise HTTPException(status_code=500, detail="Client not initialized")
             content = await opensubtitles_client.download_subtitle(int(request.file_id))
        else:
             if not subdl_client:
                  raise HTTPException(status_code=500, detail="Client not initialized")
             content = await subdl_client.download_subtitle(str(request.file_id))

        # Apply sync if specified
        if request.sync_time:
            try:
                sync_time_ms = time_string_to_ms(request.sync_time)
                content = sync_subtitles(content, sync_time_ms)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid sync time: {e}")

        # Archive
        try:
            filename = os.path.basename(request.filename)
            save_path = os.path.join(ARCHIVE_DIR, filename)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"INFO: Archived subtitle to {save_path}")
        except Exception as e:
            print(f"WARNING: Failed to archive subtitle: {e}")

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
    try:
        content = ""
        if request.provider == "opensubtitles":
             if not opensubtitles_client:
                  raise HTTPException(status_code=500, detail="Client not initialized")
             content = await opensubtitles_client.download_subtitle(int(request.file_id))
        else:
             if not subdl_client:
                  raise HTTPException(status_code=500, detail="Client not initialized")
             content = await subdl_client.download_subtitle(str(request.file_id))

        # Parse the sync time and apply
        try:
            sync_time_ms = time_string_to_ms(request.sync_time)
            synced_content = sync_subtitles(content, sync_time_ms)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid sync time format: {e}")

        # Archive
        try:
            filename = os.path.basename(request.filename)
            save_path = os.path.join(ARCHIVE_DIR, filename)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(synced_content)
            print(f"INFO: Archived synced subtitle to {save_path}")
        except Exception as e:
             print(f"WARNING: Failed to archive synced subtitle: {e}")

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
    if not translator_client:
        raise HTTPException(status_code=500, detail="Translator client not initialized")

    try:
        # Download original subtitle
        content = ""
        if request.provider == "opensubtitles":
             if not opensubtitles_client:
                  raise HTTPException(status_code=500, detail="Client not initialized")
             content = await opensubtitles_client.download_subtitle(int(request.file_id))
        else:
             if not subdl_client:
                  raise HTTPException(status_code=500, detail="Client not initialized")
             content = await subdl_client.download_subtitle(str(request.file_id))

        # Apply sync if specified (before translation)
        if request.sync_time:
            try:
                sync_time_ms = time_string_to_ms(request.sync_time)
                content = sync_subtitles(content, sync_time_ms)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid sync time: {e}")

        # Translate content
        logger.debug(f"Translating content of size {len(content)} bytes")
        translated = await translator_client.translate_subtitle_content(
            srt_content=content,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )
        logger.debug(f"Translated content size: {len(translated)} bytes")

        # Archive Result
        try:
            filename = os.path.basename(request.filename)
            save_path = os.path.join(CONVERTED_DIR, filename)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(translated)
            print(f"INFO: Archived translated subtitle to {save_path}")
        except Exception as e:
            print(f"WARNING: Failed to archive translated subtitle: {e}")

        return PlainTextResponse(
            content=translated,
            media_type="text/plain",
            headers={
                "Content-Disposition": f'attachment; filename="{request.filename}"'
            },
        )
    except ValueError as e:
         # Parsing errors
         raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# --- Archive Management Endpoints ---

class RenameRequest(BaseModel):
    filename: str
    new_filename: str
    type: str  # 'original' or 'converted'

@app.get("/api/archive/files")
async def list_archive_files(type: str = Query(..., pattern="^(original|converted)$")):
    """List files in the specified archive directory"""
    target_dir = ARCHIVE_DIR if type == "original" else CONVERTED_DIR
    
    if not os.path.exists(target_dir):
        return {"files": []}
    
    files_list = []
    try:
        # List all files
        for f in os.listdir(target_dir):
            if f.startswith('.'): continue # Skip hidden files
            
            full_path = os.path.join(target_dir, f)
            if os.path.isfile(full_path):
                stats = os.stat(full_path)
                files_list.append({
                    "name": f,
                    "size": stats.st_size,
                    "modified": stats.st_mtime,
                    "path": full_path
                })
        
        # Sort by modified time (newest first)
        files_list.sort(key=lambda x: x["modified"], reverse=True)
        return {"files": files_list}
    except Exception as e:
        logger.error(f"Failed to list archive files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/archive/rename")
async def rename_archive_file(request: RenameRequest):
    """Rename a file in the archive"""
    target_dir = ARCHIVE_DIR if request.type == "original" else CONVERTED_DIR
    
    old_path = os.path.join(target_dir, request.filename)
    new_path = os.path.join(target_dir, request.new_filename)
    
    # Validation
    if not os.path.exists(old_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    if os.path.exists(new_path):
        raise HTTPException(status_code=400, detail="A file with that name already exists")
    
    # Prevent directory traversal
    if os.path.dirname(os.path.abspath(new_path)) != os.path.abspath(target_dir):
         raise HTTPException(status_code=400, detail="Invalid filename")

    try:
        os.rename(old_path, new_path)
        logger.info(f"Renamed {request.filename} to {request.new_filename}")
        return {"status": "success", "new_name": request.new_filename}
    except Exception as e:
        logger.error(f"Failed to rename file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/archive/download/{filename}")
async def download_archive_file(filename: str, type: str = Query(..., pattern="^(original|converted)$")):
    """Download a file from the archive"""
    target_dir = ARCHIVE_DIR if type == "original" else CONVERTED_DIR
    file_path = os.path.join(target_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(
        path=file_path, 
        filename=filename,
        media_type='application/octet-stream'
    )

@app.delete("/api/archive/delete")
async def delete_archive_file(filename: str, type: str = Query(..., pattern="^(original|converted)$")):
    """Delete a file from the archive"""
    target_dir = ARCHIVE_DIR if type == "original" else CONVERTED_DIR
    file_path = os.path.join(target_dir, filename)
    
    # Validation
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Prevent directory traversal
    if os.path.dirname(os.path.abspath(file_path)) != os.path.abspath(target_dir):
         raise HTTPException(status_code=400, detail="Invalid filename")

    try:
        os.remove(file_path)
        logger.info(f"Deleted file {file_path}")
        return {"status": "success", "message": f"Deleted {filename}"}
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/languages")
async def get_languages():
    """Get list of supported languages"""
    if not translator_client:
        # Fallback if client not ready
        return [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "it", "name": "Italian"},
            {"code": "pt", "name": "Portuguese"},
            {"code": "nl", "name": "Dutch"},
            {"code": "ru", "name": "Russian"},
            {"code": "zh", "name": "Chinese"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "tr", "name": "Turkish"},
            {"code": "th", "name": "Thai"},
        ]

    try:
        return await translator_client.get_languages()
    except Exception as e:
        logger.error(f"Failed to fetch languages: {e}")
         # Fallback
        return [
            {"code": "en", "name": "English"},
            {"code": "th", "name": "Thai"},
             {"code": "tr", "name": "Turkish"},
        ]



class ArchiveTranslateRequest(BaseModel):
    filename: str
    source_lang: str
    target_lang: str
    sync_time: Optional[str] = None

@app.post("/api/archive/translate")
async def translate_archive_file(request: ArchiveTranslateRequest):
    """Translate a file from the archive"""
    file_path = os.path.join(ARCHIVE_DIR, request.filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found in archive")

    try:
        # Read content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check content length
        if not content.strip():
             raise HTTPException(status_code=400, detail="File is empty")

        # Sync if needed
        if request.sync_time:
            # Re-using sync logic requires parsing blocks first, but `sync_subtitles` takes blocks.
            # TranslatorClient parses internally.
            # Ideally we reuse the pipeline: Parse -> Sync -> Translate -> Build.
            # Current `TranslatorClient` does Parse -> Translate -> Build.
            # `sync_subtitles` does Blocks -> Blocks.
            # So we should Parse -> Sync -> Translate.
            # But `TranslatorClient` encapsulates parsing. 
            # Let's adjust TranslatorClient or handle manually here?
            # Simpler: If sync is requested, we might need to parse here.
            # But wait, `main.py` `translate_subtitle` endpoint handles sync BEFORE passing to translator?
            # No, `translate_subtitle` reads `content`, shifts it if `sync_time` is present, then passes to translator.
            pass

        # Handle Sync
        if request.sync_time:
             # We need to temporarily parse, sync, then rebuild or just pass raw content if we had a better pipeline.
             # Existing `shift_subtitles` takes file path or content? 
             # `shift_subtitles` takes `blocks` and `shift_ms`.
             # `translator.py` has `_parse_srt`.
             # Let's use translator client to parse, then sync, then translate?
             # `TranslatorClient` has `translate_subtitle_content` which takes STR.
             # So we should Parse -> Sync -> Build String -> Translate.
             
             # Re-implement small sync pipeline here or refactor.
             # For speed, let's reuse `translator_client._parse_srt` and `_build_srt` if public, or just duplicate small logic?
             # Better: `translator_client` is available.
             blocks = translator_client._parse_srt(content)
             
             # Calculate shift (copied from `translate_subtitle`)
             # We need to find the first block's start time to calculate offset.
             if blocks:
                 first_block_start = blocks[0]['timing']['start_ms']
                 target_start_ms = time_string_to_ms(request.sync_time)
                 if target_start_ms is not None:
                     shift_amount = target_start_ms - first_block_start
                     blocks = shift_subtitles(blocks, shift_amount)
                     # Rebuild content for translation
                     content = translator_client._build_srt(blocks)

        # Translate
        translated = await translator_client.translate_subtitle_content(
            srt_content=content,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )

        # Save to Converted
        # Construct new filename: Original_Lang.srt
        base_name = os.path.splitext(request.filename)[0]
        new_filename = f"{base_name}_{request.target_lang}.srt"
        save_path = os.path.join(CONVERTED_DIR, new_filename)
        
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(translated)
            
        logger.info(f"Translated archive file {request.filename} to {save_path}")
        
        return {
            "status": "success", 
            "message": f"Translated to {new_filename}",
            "filename": new_filename
        }

    except Exception as e:
        logger.error(f"Failed to translate archive file: {e}")
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
