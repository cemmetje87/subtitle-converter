# Subtitle Converter

A web application to search, download, and translate subtitles from OpenSubtitles.org using LibreTranslate.

## Features

- 🔍 **Search subtitles** from OpenSubtitles.org in any language
- 📥 **Download** subtitles directly
- 🌐 **Translate** subtitles from English to any supported language using LibreTranslate
- ⏱️ **Timing sync** - adjust subtitle timing to match your video
- 🎨 **Modern UI** with dark glassmorphism design

## Quick Start with Docker (Recommended)

1. **Configure your API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENSUBTITLES_API_KEY
   ```

2. **Start everything:**
   ```bash
   docker compose up -d
   ```

3. **Open in browser:** [http://localhost:8000](http://localhost:8000)

4. **Stop when done:**
   ```bash
   docker compose down
   ```

## Manual Setup (Without Docker)

### Prerequisites
- Python 3.11+
- [uv](https://astral.sh/uv) package manager
- OpenSubtitles API key ([get one here](https://www.opensubtitles.com/en/consumers))

### Steps

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Start LibreTranslate** (for translation):
   ```bash
   docker run -d --name libretranslate -p 5000:5000 libretranslate/libretranslate
   ```

4. **Run the application:**
   ```bash
   uv run uvicorn src.main:app --reload
   ```

5. **Open in browser:** [http://localhost:8000](http://localhost:8000)

## Usage

1. Enter a movie or TV show name
2. Select the subtitle language
3. Click **Search Subtitles**
4. Optionally enter a sync time (e.g., `120` seconds) to adjust timing
5. Click **Download** or **Translate**

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/languages` | List available subtitle languages |
| GET | `/api/translation-languages` | List translation languages |
| GET | `/api/search` | Search subtitles |
| POST | `/api/download` | Download subtitle (with optional sync) |
| POST | `/api/sync` | Download with timing sync |
| POST | `/api/translate` | Translate and download |

## Tech Stack

- **Backend:** FastAPI, Python, httpx
- **Frontend:** HTML, CSS, JavaScript
- **APIs:** OpenSubtitles.org, LibreTranslate
- **Deployment:** Docker, Docker Compose

## License

MIT
