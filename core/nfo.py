import os
import logging
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent

from core.datatype import MovieInfo

logger = logging.getLogger(__name__)


def _add_element(parent: Element, tag: str, text: str = None):
    """Add a child element with optional text content."""
    el = SubElement(parent, tag)
    if text is not None:
        el.text = str(text)
    return el


def generate_nfo(movie: MovieInfo, nfo_path: str):
    """Generate a Kodi/Jellyfin/Emby compatible NFO file."""
    root = Element('movie')

    _add_element(root, 'title', movie.title)
    _add_element(root, 'originaltitle', movie.original_title)
    _add_element(root, 'year', movie.year)
    _add_element(root, 'plot', movie.plot or movie.outline)
    _add_element(root, 'outline', movie.outline)
    _add_element(root, 'runtime', movie.runtime)
    _add_element(root, 'premiered', movie.publish_date)
    _add_element(root, 'studio', movie.studio)
    _add_element(root, 'director', movie.director)

    if movie.rating is not None:
        ratings_el = _add_element(root, 'ratings')
        rating_el = _add_element(ratings_el, 'rating')
        rating_el.set('name', 'default')
        rating_el.set('default', 'true')
        _add_element(rating_el, 'value', f'{movie.rating:.1f}')
        if movie.votes:
            _add_element(rating_el, 'votes', str(movie.votes))

    for genre in movie.genre:
        _add_element(root, 'genre', genre)

    for name in movie.actor:
        actor_el = _add_element(root, 'actor')
        _add_element(actor_el, 'name', name)

    for country in movie.country:
        _add_element(root, 'country', country)

    for lang in movie.language:
        _add_element(root, 'language', lang)

    if movie.tmdb_id:
        uid = _add_element(root, 'uniqueid', movie.tmdb_id)
        uid.set('type', 'tmdb')
    if movie.imdb_id:
        uid = _add_element(root, 'uniqueid', movie.imdb_id)
        uid.set('type', 'imdb')
    if movie.douban_id:
        uid = _add_element(root, 'uniqueid', movie.douban_id)
        uid.set('type', 'douban')

    if movie.trailer:
        _add_element(root, 'trailer', movie.trailer)

    if movie.cover:
        art = _add_element(root, 'art')
        _add_element(art, 'poster', movie.cover)
        if movie.backdrop:
            _add_element(art, 'fanart', movie.backdrop)

    tree = ElementTree(root)
    indent(tree, space='  ')

    os.makedirs(os.path.dirname(nfo_path), exist_ok=True)
    tree.write(nfo_path, encoding='utf-8', xml_declaration=True)
    logger.info(f"NFO saved: {nfo_path}")
