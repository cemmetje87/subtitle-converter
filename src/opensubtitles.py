"""OpenSubtitles.org API Client"""

import httpx
from typing import Optional


class OpenSubtitlesClient:
    """Client for interacting with OpenSubtitles.org REST API"""

    BASE_URL = "https://api.opensubtitles.com/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.token: Optional[str] = None
        self.headers = {
            "Api-Key": api_key,
            "Content-Type": "application/json",
            "User-Agent": "SubtitleConverter v1.0",
        }

    async def search_subtitles(
        self,
        query: str = "",
        languages: str = "en",
        imdb_id: Optional[str] = None,
        tmdb_id: Optional[str] = None,
        year: Optional[int] = None,
        season_number: Optional[int] = None,
        episode_number: Optional[int] = None,
    ) -> dict:
        """
        Search for subtitles on OpenSubtitles.org

        Args:
            query: Movie/show name to search
            languages: Comma-separated language codes (e.g., "en,th,es")
            imdb_id: IMDB ID (without 'tt' prefix)
            tmdb_id: TMDB ID
            year: Release year
            season_number: Season number for TV shows
            episode_number: Episode number for TV shows

        Returns:
            Search results from OpenSubtitles API
        """
        params = {}

        if query:
            params["query"] = query
        if languages:
            params["languages"] = languages
        if imdb_id:
            params["imdb_id"] = imdb_id
        if tmdb_id:
            params["tmdb_id"] = tmdb_id
        if year:
            params["year"] = year
        if season_number is not None:
            params["season_number"] = season_number
        if episode_number is not None:
            params["episode_number"] = episode_number

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.BASE_URL}/subtitles",
                headers=self.headers,
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_download_link(self, file_id: int) -> dict:
        """
        Get download link for a subtitle file

        Args:
            file_id: The file_id from search results

        Returns:
            Download info including the link
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{self.BASE_URL}/download",
                headers=self.headers,
                json={"file_id": file_id},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def download_subtitle(self, file_id: int) -> str:
        """
        Download subtitle content

        Args:
            file_id: The file_id from search results

        Returns:
            SRT file content as string
        """
        download_info = await self.get_download_link(file_id)
        download_url = download_info.get("link")

        if not download_url:
            raise ValueError("No download link received from API")

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(download_url, timeout=60.0)
            response.raise_for_status()
            return response.text

    async def get_languages(self) -> list:
        """
        Get list of available languages

        Returns:
            List of language objects with code and name
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.BASE_URL}/infos/languages",
                headers=self.headers,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json().get("data", [])
