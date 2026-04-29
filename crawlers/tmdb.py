"""TMDb (The Movie Database) crawler.

Requires a free API key from https://www.themoviedb.org/settings/api
"""
import logging

from core.config import cfg
from core.datatype import MovieInfo
from crawlers.base import Request, MovieNotFoundError, CrawlerError

logger = logging.getLogger(__name__)

API_BASE = 'https://api.themoviedb.org/3'
IMG_BASE = 'https://image.tmdb.org/t/p'

request = Request(
    proxy=cfg.Network.proxy if cfg.Network.use_proxy.lower() == 'yes' else None,
    timeout=int(cfg.Network.timeout),
    retry=int(cfg.Network.retry),
)


def _api_key() -> str:
    key = cfg.Crawler.tmdb_api_key
    if not key:
        raise CrawlerError("TMDb API key not configured. Get one at https://www.themoviedb.org/settings/api")
    return key


def _lang() -> str:
    return cfg.Crawler.tmdb_language


def search_movie(title: str, year: str = None) -> list[dict]:
    """Search TMDb for movies matching title and optional year."""
    params = {
        'api_key': _api_key(),
        'query': title,
        'language': _lang(),
    }
    if year:
        params['year'] = year
    data = request.get_json(f'{API_BASE}/search/movie', params=params)
    return data.get('results', [])


def parse_data(movie: MovieInfo):
    """Fetch movie metadata from TMDb."""
    # Step 1: Find the movie
    if movie.tmdb_id:
        tmdb_id = movie.tmdb_id
    else:
        title = movie.title or movie.original_title
        if not title:
            raise CrawlerError("No title available for TMDb search")
        results = search_movie(title, movie.year)
        if not results:
            # Retry without year
            results = search_movie(title)
        if not results:
            raise MovieNotFoundError('tmdb', title)
        tmdb_id = str(results[0]['id'])

    # Step 2: Get movie details
    params = {'api_key': _api_key(), 'language': _lang(), 'append_to_response': 'credits,videos'}
    data = request.get_json(f'{API_BASE}/movie/{tmdb_id}', params=params)

    movie.tmdb_id = str(data['id'])
    movie.imdb_id = data.get('imdb_id')
    movie.title = data.get('title')
    movie.original_title = data.get('original_title')
    movie.plot = data.get('overview')
    movie.year = data.get('release_date', '')[:4] or None
    movie.publish_date = data.get('release_date')
    movie.runtime = str(data['runtime']) if data.get('runtime') else None
    movie.rating = data.get('vote_average')
    movie.votes = data.get('vote_count')
    movie.genre = [g['name'] for g in data.get('genres', [])]
    movie.country = [c['name'] for c in data.get('production_countries', [])]
    movie.language = [l['english_name'] for l in data.get('spoken_languages', [])]
    movie.url = f'https://www.themoviedb.org/movie/{tmdb_id}'

    if data.get('production_companies'):
        movie.studio = data['production_companies'][0]['name']

    # Cover and backdrop
    if data.get('poster_path'):
        res = 'original' if cfg.Picture.use_high_res_cover.lower() == 'yes' else 'w500'
        movie.cover = f'{IMG_BASE}/{res}{data["poster_path"]}'
    if data.get('backdrop_path'):
        movie.backdrop = f'{IMG_BASE}/original{data["backdrop_path"]}'

    # Credits: director and top actors
    credits = data.get('credits', {})
    for crew in credits.get('crew', []):
        if crew.get('job') == 'Director':
            movie.director = crew['name']
            break
    movie.actor = [c['name'] for c in credits.get('cast', [])[:15]]

    # Trailer
    for video in data.get('videos', {}).get('results', []):
        if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
            movie.trailer = f'https://www.youtube.com/watch?v={video["key"]}'
            break

    movie.source = 'tmdb'
    logger.info(f"[TMDb] Scraped: {movie.title} ({movie.year})")


if __name__ == "__main__":
    m = MovieInfo(title='Inception')
    parse_data(m)
    print(m)
