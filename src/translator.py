"""LibreTranslate API Client for subtitle translation"""

import httpx
from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)

class TranslatorClient:
    """Client for interacting with LibreTranslate API"""

    def __init__(self, base_url: str = "http://localhost:5000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def get_languages(self) -> list:
        """
        Get list of supported languages

        Returns:
            List of language objects with code and name
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/languages", timeout=30.0)
            response.raise_for_status()
            return response.json()

    async def translate_text(self, text: str, source: str, target: str) -> str:
        """
        Translate a single text string

        Args:
            text: Text to translate
            source: Source language code (e.g., "en")
            target: Target language code (e.g., "th")

        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text

        payload = {
            "q": text,
            "source": source,
            "target": target,
            "format": "text",
        }

        # logger.info(f"Translating: {text[:50]}...") 

        if self.api_key:
            payload["api_key"] = self.api_key

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/translate",
                json=payload,
                timeout=60.0,
            )
            if response.status_code != 200:
                logger.error(f"Translation failed: {response.status_code} - {response.text}")
                logger.error(f"Payload: {payload}")
                
            response.raise_for_status()
            result = response.json()
            return result.get("translatedText", "")

    async def translate_subtitle_content(
        self,
        srt_content: str,
        source_lang: str,
        target_lang: str,
        progress_callback=None,
    ) -> str:
        """
        Translate entire SRT subtitle content

        Args:
            srt_content: Raw SRT file content
            source_lang: Source language code
            target_lang: Target language code
            progress_callback: Optional async callback(current, total)

        Returns:
            Translated SRT content
        """
        # Parse SRT content
        blocks = self._parse_srt(srt_content)
        total_blocks = len(blocks)

        translated_blocks = []
        for i, block in enumerate(blocks):
            # Translate only the text portion, keep timing intact
            translated_text = await self.translate_text(
                block["text"], source_lang, target_lang
            )

            translated_blocks.append({
                "index": block["index"],
                "timing": block["timing"],
                "text": translated_text,
            })

            if progress_callback:
                await progress_callback(i + 1, total_blocks)

        return self._build_srt(translated_blocks)

    def _parse_srt(self, content: str) -> list:
        """Parse SRT content into blocks"""
        blocks = []
        # Normalise line endings using simple replace, to handle mixed/windows endings safely
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove BOM if present (utf-8-sig in subdl generally handles this, but good to be safe)
        if content.startswith('\ufeff'):
            content = content[1:]

        # Split by double newline (block separator)
        # Regex explanation: \n followed by any whitespace (including newlines) followed by \n
        # This handles \n\n, \n  \n, \n\r\n etc (though we normalized already)
        raw_blocks = re.split(r'\n\s*\n', content.strip())
        logger.debug(f"Parser found {len(raw_blocks)} raw blocks")

        for raw_block in raw_blocks:
            lines = raw_block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0].strip())
                    timing = lines[1].strip()
                    text = '\n'.join(lines[2:])
                    blocks.append({
                        "index": index,
                        "timing": timing,
                        "text": text,
                    })
                except ValueError:
                    # Skip malformed blocks
                    continue

        # Validate parsing results
        if not blocks:
            # Check for common unsupported formats signature
            signature = content[:50].strip()
            error_msg = "No valid subtitle blocks found. "
            if "<SAMI>" in signature or "<HEAD>" in signature:
                error_msg += "Format appears to be SAMI (.smi) which is not supported."
            elif "{1}" in signature:
                error_msg += "Format appears to be MicroDVD (.sub) which is not supported."
            else:
                error_msg += "Format invalid or not supported (only SRT is supported)."
            
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.debug(f"Parser validated {len(blocks)} blocks")
        return blocks

    def _build_srt(self, blocks: list) -> str:
        """Build SRT content from blocks"""
        output_lines = []
        for block in blocks:
            output_lines.append(str(block["index"]))
            output_lines.append(block["timing"])
            output_lines.append(block["text"])
            output_lines.append("")  # Empty line separator

        return '\n'.join(output_lines)
