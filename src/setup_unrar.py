import os
import tarfile
import httpx
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

UNRAR_URL = "https://www.rarlab.com/rar/rarlinux-x64-701.tar.gz"
PROJECT_ROOT = Path(__file__).parent.parent
BIN_DIR = PROJECT_ROOT / "bin"
UNRAR_PATH = BIN_DIR / "unrar"

def setup_unrar() -> str:
    """
    Ensure unrar binary exists in bin/ directory.
    Downloads it if missing.
    Returns absolute path to unrar executable.
    """
    if not BIN_DIR.exists():
        BIN_DIR.mkdir(parents=True, exist_ok=True)

    if UNRAR_PATH.exists():
        return str(UNRAR_PATH.absolute())

    logger.info("Downloading unrar from %s...", UNRAR_URL)
    
    try:
        # Download the tar.gz
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(UNRAR_URL)
            response.raise_for_status()
            
            tar_path = BIN_DIR / "unrar.tar.gz"
            with open(tar_path, "wb") as f:
                f.write(response.content)

        # Extract
        logger.info("Extracting unrar...")
        with tarfile.open(tar_path, "r:gz") as tar:
            # The tar contains a folder 'rar/'. We need 'rar/unrar'
            try:
                member = tar.getmember("rar/unrar")
                member.name = "unrar" # Extract named as just unrar
                tar.extract(member, path=BIN_DIR)
            except KeyError:
                # Fallback implementation if specific member extraction differs
                tar.extractall(path=BIN_DIR)
                # Should be at bin/rar/unrar
                extracted_path = BIN_DIR / "rar" / "unrar"
                if extracted_path.exists():
                    shutil.move(str(extracted_path), str(UNRAR_PATH))
                    shutil.rmtree(BIN_DIR / "rar")

        # Cleanup tar
        if tar_path.exists():
            tar_path.unlink()

        # Make executable
        UNRAR_PATH.chmod(0o755)
        
        logger.info("Unrar setup complete at %s", UNRAR_PATH)
        return str(UNRAR_PATH.absolute())

    except Exception as e:
        logger.error("Failed to setup unrar: %s", e)
        # Attempt cleanup
        if tar_path.exists():
            tar_path.unlink()
        raise
