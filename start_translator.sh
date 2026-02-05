#!/bin/bash
echo "Starting LibreTranslate on port 5050..."
# Assuming installed via uv in the project environment
# LibreTranslate usually provides a CLI `libretranslate`
# running with uv run ensures we use the project environment
/home/cozugur/.local/bin/uv run libretranslate --host 0.0.0.0 --port 5050 --load-only en,th,nl,tr
