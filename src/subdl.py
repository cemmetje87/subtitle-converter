import httpx
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SubDLClient:
    BASE_URL = "https://api.subdl.com/api/v1/subtitles"
    DOWNLOAD_BASE_URL = "https://dl.subdl.com"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search_subtitles(
        self,
        query: str,
        languages: str = "en",
        imdb_id: Optional[str] = None,
        year: Optional[int] = None,
        season_number: Optional[int] = None,
        episode_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Search for subtitles on SubDL.
        """
        params = {
            "api_key": self.api_key,
            "subs_per_page": 30,
        }

        # Handle languages
        # SubDL expects comma separated full language names or codes? 
        # a4kSubtitles implementation suggests it maps them. 
        # For simplicity, we'll pass what we get, but ideally we might need mapping.
        # However, looking at a4kSubtitles: 'languages': ','.join(lang_ids)
        params["languages"] = languages

        if season_number and episode_number:
            params["type"] = "tv"
            params["film_name"] = query
            params["season_number"] = season_number
            params["episode_number"] = episode_number
            if year:
                params["year"] = year
        else:
            params["type"] = "movie"
            if imdb_id:
                params["imdb_id"] = imdb_id
                # If we have imdb_id, we might not need query, but let's see.
                # a4kSubtitles uses imdb_id and year for movies.
            
            if year:
                params["year"] = year
            
            if query and not imdb_id:
                 params["film_name"] = query

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("status"):
                    logger.error(f"SubDL error: {data.get('message')}")
                    return {"results": []}

                subtitles = data.get("subtitles", [])
                
                # Normalize results to match OpenSubtitles format roughly
                normalized_results = []
                for sub in subtitles:
                    # SubDL returns 'url' which is a relative path like /subtitle/3189858-3200938.zip
                    # And 'release_name', 'language', 'hi' (hearing impaired)
                    
                    normalized_results.append({
                        "id": sub.get("url"), # Use URL as ID strictly for download retrieval
                        "filename": sub.get("release_name", "Unknown"),
                        "language": sub.get("language"),
                        "url": f"{self.DOWNLOAD_BASE_URL}{sub.get('url')}",
                        "is_hearing_impaired": sub.get("hi", False),
                        "source": "SubDL"
                    })
                
                return {"results": normalized_results}

            except Exception as e:
                logger.error(f"Error searching SubDL: {e}")
                return {"results": [], "error": str(e)}

    async def download_subtitle(self, file_url_or_id: str) -> str:
        """
        Download subtitle content. 
        """
        # If the ID passed is the relative URL
        url = file_url_or_id
        if not url.startswith("http"):
             url = f"{self.DOWNLOAD_BASE_URL}{file_url_or_id}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            content_type = response.headers.get("content-type", "")
            
            # Check if it's a zip or rar
            if "zip" in content_type or url.endswith(".zip"):
                import io
                import zipfile
                import rarfile
                
                content_io = io.BytesIO(response.content)
                
                # Try ZIP first
                try:
                    with zipfile.ZipFile(content_io) as z:
                        for file in z.namelist():
                            if file.endswith(".srt"):
                                return z.read(file).decode("utf-8-sig", errors="replace")
                        if z.namelist():
                             return z.read(z.namelist()[0]).decode("utf-8-sig", errors="replace")
                except zipfile.BadZipFile:
                    # Try RAR (SubDL often returns RAR named as ZIP)
                    try:
                        content_io.seek(0)
                        with rarfile.RarFile(content_io) as r:
                            for file in r.namelist():
                                if file.endswith(".srt"):
                                    return r.read(file).decode("utf-8-sig", errors="replace")
                            if r.namelist():
                                return r.read(r.namelist()[0]).decode("utf-8-sig", errors="replace")
                    except Exception as e:
                        logger.error(f"Failed to extract content from {url} as ZIP or RAR: {e}")
                        raise ValueError("File is not a valid zip or rar file")
            
            return response.text
