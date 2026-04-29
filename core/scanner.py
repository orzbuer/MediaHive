import os
import re
import logging
from typing import Optional

from core.config import cfg

logger = logging.getLogger(__name__)

MEDIA_EXT = set(cfg.File.media_ext.split(';'))
IGNORE_FOLDERS = set(cfg.File.ignore_folder.split(';'))
IGNORE_WORDS = [w.strip() for w in cfg.MovieID.ignore_words.split(';') if w.strip()]
MIN_SIZE = int(cfg.File.ignore_file_less_than) * 1024 * 1024

# Common patterns: "Movie Name (2020)", "Movie.Name.2020.1080p", "Movie Name [2020]"
_YEAR_PATTERNS = [
    re.compile(r'[\(\[（](\d{4})[\)\]）]'),
    re.compile(r'[\.\s_-](\d{4})[\.\s_-]'),
    re.compile(r'[\.\s_-](\d{4})$'),
]


def scan_directory(scan_dir: str) -> list[dict]:
    """Scan a directory for video files and return a list of file info dicts."""
    results = []
    if not os.path.isdir(scan_dir):
        logger.error(f"Directory not found: {scan_dir}")
        return results

    for root, dirs, files in os.walk(scan_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS and not d.startswith('.')]
        for fname in files:
            ext = fname.rsplit('.', 1)[-1].lower() if '.' in fname else ''
            if ext not in MEDIA_EXT:
                continue
            filepath = os.path.join(root, fname)
            fsize = os.path.getsize(filepath)
            if MIN_SIZE > 0 and fsize < MIN_SIZE:
                logger.debug(f"Skipped (too small): {filepath}")
                continue
            results.append({
                'file_path': filepath,
                'file_name': fname,
                'file_size': fsize,
            })
    logger.info(f"Found {len(results)} video files in {scan_dir}")
    return results


def guess_title_and_year(filename: str) -> tuple[Optional[str], Optional[str]]:
    """Guess movie title and year from a filename."""
    name = filename.rsplit('.', 1)[0] if '.' in filename else filename

    for word in IGNORE_WORDS:
        name = re.sub(re.escape(word), ' ', name, flags=re.IGNORECASE)

    year = None
    for pattern in _YEAR_PATTERNS:
        m = pattern.search(name)
        if m:
            y = int(m.group(1))
            if 1900 <= y <= 2099:
                year = str(y)
                name = name[:m.start()] + name[m.end():]
                break

    name = re.sub(r'[\.\-_\[\]【】]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    # Remove trailing quality/source tags
    name = re.sub(r'\b(BluRay|BDRip|HDRip|WEB[- ]?DL|WEBRip|HDTV|REMUX|x26[45]|HEVC|AAC|DTS|10bit)\b.*',
                  '', name, flags=re.IGNORECASE).strip()

    title = name if name else None
    return title, year
