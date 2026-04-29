import os
import re
import shutil
import logging
from string import Template

from core.config import cfg
from core.datatype import MovieInfo
from core.nfo import generate_nfo
from core.image import save_poster, save_backdrop

logger = logging.getLogger(__name__)


def _safe_filename(name: str) -> str:
    """Remove characters that are invalid in filenames."""
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()


def _build_path(pattern: str, movie: MovieInfo) -> str:
    """Substitute movie fields into a naming pattern."""
    mapping = {
        'title': _safe_filename(movie.title or cfg.NamingRule.null_for_title),
        'original_title': _safe_filename(movie.original_title or movie.title or ''),
        'year': movie.year or 'Unknown',
        'director': _safe_filename(movie.director or cfg.NamingRule.null_for_director),
        'rating': f'{movie.rating:.1f}' if movie.rating else '',
        'studio': _safe_filename(movie.studio or ''),
    }
    result = pattern
    for key, val in mapping.items():
        result = result.replace(f'${key}', val)
    return result


def organize_movie(movie: MovieInfo, output_root: str = None):
    """Organize a single movie: create folder, move file, save NFO and images."""
    if not movie.file_path or not os.path.isfile(movie.file_path):
        logger.error(f"Source file not found: {movie.file_path}")
        return

    if output_root is None:
        output_root = os.path.join(os.path.dirname(movie.file_path), cfg.NamingRule.output_folder)

    folder_name = _build_path(cfg.NamingRule.save_dir, movie)
    base_name = _build_path(cfg.NamingRule.filename, movie)
    dest_dir = os.path.join(output_root, folder_name)
    os.makedirs(dest_dir, exist_ok=True)

    # Move video file
    ext = os.path.splitext(movie.file_path)[1]
    dest_file = os.path.join(dest_dir, _safe_filename(base_name) + ext)
    if cfg.File.enable_file_move.lower() == 'yes':
        if os.path.abspath(movie.file_path) != os.path.abspath(dest_file):
            shutil.move(movie.file_path, dest_file)
            logger.info(f"Moved: {movie.file_path} -> {dest_file}")
            movie.file_path = dest_file

    # Save NFO
    nfo_path = os.path.join(dest_dir, _safe_filename(base_name) + '.nfo')
    generate_nfo(movie, nfo_path)

    # Save poster
    save_poster(movie.cover, dest_dir)

    # Save backdrop
    if cfg.Picture.download_backdrop.lower() == 'yes':
        save_backdrop(movie.backdrop, dest_dir)

    logger.info(f"Organized: {movie.title} ({movie.year}) -> {dest_dir}")
