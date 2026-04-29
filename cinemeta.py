#!/usr/bin/env python3
"""MediaHive - Multi-source movie metadata scraper and media organizer.

Scans local video files, fetches metadata from TMDb and Douban,
generates Jellyfin/Emby/Plex compatible NFO files, and organizes
your movie library automatically.
"""
import os
import sys
import time
import logging
import importlib
import argparse

from tqdm import tqdm

from core.config import cfg
from core.datatype import MovieInfo
from core.scanner import scan_directory, guess_title_and_year
from core.organizer import organize_movie

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('cinemeta.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)


def load_crawlers() -> list:
    """Dynamically load crawlers based on config."""
    crawler_names = [c.strip() for c in cfg.CrawlerSelect.crawlers.split(',')]
    crawlers = []
    for name in crawler_names:
        try:
            mod = importlib.import_module(f'crawlers.{name}')
            if hasattr(mod, 'parse_data'):
                crawlers.append((name, mod.parse_data))
                logger.debug(f"Loaded crawler: {name}")
        except ImportError as e:
            logger.warning(f"Failed to load crawler '{name}': {e}")
    return crawlers


def scrape_movie(movie: MovieInfo, crawlers: list) -> bool:
    """Scrape metadata from multiple sources and merge results."""
    required_keys = [k.strip() for k in cfg.Crawler.required_keys.split(',')]
    sleep_time = float(cfg.Crawler.sleep_after_scraping)

    for name, parse_fn in crawlers:
        try:
            result = MovieInfo()
            result.title = movie.title
            result.original_title = movie.original_title
            result.year = movie.year
            result.tmdb_id = movie.tmdb_id
            result.douban_id = movie.douban_id
            parse_fn(result)
            movie.merge(result)
            logger.info(f"[{name}] Success: {movie.title}")
        except Exception as e:
            logger.debug(f"[{name}] Failed for '{movie.title}': {e}")

    if sleep_time > 0:
        time.sleep(sleep_time)

    return movie.has_required_keys(required_keys)


def process_directory(scan_dir: str):
    """Main pipeline: scan -> scrape -> organize."""
    logger.info(f"Scanning directory: {scan_dir}")
    files = scan_directory(scan_dir)
    if not files:
        logger.info("No video files found.")
        return

    crawlers = load_crawlers()
    if not crawlers:
        logger.error("No crawlers available. Check your config and API keys.")
        return

    success, failed = 0, 0
    for finfo in tqdm(files, desc='Processing', unit='file'):
        title, year = guess_title_and_year(finfo['file_name'])
        if not title:
            logger.warning(f"Cannot guess title from: {finfo['file_name']}")
            failed += 1
            continue

        movie = MovieInfo(
            title=title,
            year=year,
            file_path=finfo['file_path'],
            file_size=finfo['file_size'],
        )

        if scrape_movie(movie, crawlers):
            organize_movie(movie)
            success += 1
        else:
            logger.warning(f"Insufficient data for: {finfo['file_name']}")
            failed += 1

    logger.info(f"Done. Success: {success}, Failed: {failed}, Total: {len(files)}")


def main():
    parser = argparse.ArgumentParser(
        description='MediaHive - Movie metadata scraper and media organizer',
    )
    parser.add_argument('directory', nargs='?', default=None,
                        help='Directory to scan for video files')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable debug logging')
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    scan_dir = args.directory or cfg.File.scan_dir
    if not scan_dir:
        scan_dir = input("Enter directory to scan: ").strip()
    if not scan_dir or not os.path.isdir(scan_dir):
        logger.error(f"Invalid directory: {scan_dir}")
        sys.exit(1)

    process_directory(scan_dir)


if __name__ == '__main__':
    main()
