import os
import logging

import requests

logger = logging.getLogger(__name__)


def download_image(url: str, save_path: str, timeout: int = 15) -> bool:
    """Download an image from URL and save to disk."""
    try:
        r = requests.get(url, timeout=timeout, stream=True)
        r.raise_for_status()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Image saved: {save_path}")
        return True
    except Exception as e:
        logger.warning(f"Failed to download image {url}: {e}")
        return False


def save_poster(cover_url: str, dest_dir: str, filename: str = 'poster') -> str | None:
    """Download and save the poster image. Returns the saved file path or None."""
    if not cover_url:
        return None
    ext = _guess_ext(cover_url)
    save_path = os.path.join(dest_dir, f'{filename}{ext}')
    if download_image(cover_url, save_path):
        return save_path
    return None


def save_backdrop(backdrop_url: str, dest_dir: str, filename: str = 'fanart') -> str | None:
    """Download and save the backdrop/fanart image."""
    if not backdrop_url:
        return None
    ext = _guess_ext(backdrop_url)
    save_path = os.path.join(dest_dir, f'{filename}{ext}')
    if download_image(backdrop_url, save_path):
        return save_path
    return None


def _guess_ext(url: str) -> str:
    """Guess image file extension from URL."""
    path = url.split('?')[0]
    if '.' in path:
        ext = '.' + path.rsplit('.', 1)[-1].lower()
        if ext in ('.jpg', '.jpeg', '.png', '.webp'):
            return ext
    return '.jpg'
