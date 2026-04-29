"""Douban movie crawler.

Scrapes movie metadata from douban.com via HTML parsing.
No API key required, but subject to rate limiting.
"""
import re
import logging

from core.datatype import MovieInfo
from crawlers.base import Request, MovieNotFoundError

logger = logging.getLogger(__name__)

SEARCH_URL = 'https://www.douban.com/search'
MOVIE_URL = 'https://movie.douban.com/subject/{douban_id}/'

request = Request(timeout=10, retry=3)
request.session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
})


def search_movie(title: str, year: str = None) -> str | None:
    """Search Douban for a movie and return its subject ID."""
    query = f'{title} {year}' if year else title
    html = request.get_html(SEARCH_URL, params={'cat': '1002', 'q': query})
    links = html.xpath('//div[@class="result"]//div[@class="title"]/h3/a/@href')
    for link in links:
        m = re.search(r'subject/(\d+)', link)
        if m:
            return m.group(1)
    return None


def parse_data(movie: MovieInfo):
    """Fetch movie metadata from Douban."""
    # Step 1: Find the movie
    if movie.douban_id:
        douban_id = movie.douban_id
    else:
        title = movie.title or movie.original_title
        if not title:
            return
        douban_id = search_movie(title, movie.year)
        if not douban_id:
            raise MovieNotFoundError('douban', title)

    # Step 2: Get movie page
    url = MOVIE_URL.format(douban_id=douban_id)
    html = request.get_html(url)

    movie.douban_id = douban_id
    movie.url = movie.url or url

    # Title
    title_el = html.xpath('//span[@property="v:itemreviewed"]/text()')
    if title_el:
        movie.title = movie.title or title_el[0].strip()

    # Year
    year_el = html.xpath('//span[@class="year"]/text()')
    if year_el:
        m = re.search(r'(\d{4})', year_el[0])
        if m:
            movie.year = movie.year or m.group(1)

    # Rating
    rating_el = html.xpath('//strong[@property="v:average"]/text()')
    if rating_el and rating_el[0].strip():
        try:
            movie.rating = movie.rating or float(rating_el[0].strip())
        except ValueError:
            pass

    votes_el = html.xpath('//span[@property="v:votes"]/text()')
    if votes_el:
        try:
            movie.votes = movie.votes or int(votes_el[0])
        except ValueError:
            pass

    # Director
    director_el = html.xpath('//a[@rel="v:directedBy"]/text()')
    if director_el:
        movie.director = movie.director or director_el[0]

    # Actors
    actor_els = html.xpath('//a[@rel="v:starring"]/text()')
    if actor_els and not movie.actor:
        movie.actor = actor_els[:15]

    # Genre
    genre_els = html.xpath('//span[@property="v:genre"]/text()')
    if genre_els and not movie.genre:
        movie.genre = genre_els

    # Runtime
    runtime_el = html.xpath('//span[@property="v:runtime"]/@content')
    if runtime_el:
        movie.runtime = movie.runtime or runtime_el[0]

    # Release date
    date_el = html.xpath('//span[@property="v:initialReleaseDate"]/@content')
    if date_el:
        movie.publish_date = movie.publish_date or date_el[0].split('(')[0]

    # Plot
    plot_el = html.xpath('//span[@property="v:summary"]/text()')
    if plot_el:
        plot = '\n'.join(p.strip() for p in plot_el).strip()
        movie.plot = movie.plot or plot

    # Cover
    cover_el = html.xpath('//img[@rel="v:image"]/@src')
    if cover_el:
        movie.cover = movie.cover or cover_el[0]

    # Info block for country and language
    info_text = html.xpath('//div[@id="info"]')[0].text_content() if html.xpath('//div[@id="info"]') else ''
    country_m = re.search(r'制片国家/地区:\s*(.+)', info_text)
    if country_m and not movie.country:
        movie.country = [c.strip() for c in country_m.group(1).split('/')]
    lang_m = re.search(r'语言:\s*(.+)', info_text)
    if lang_m and not movie.language:
        movie.language = [l.strip() for l in lang_m.group(1).split('/')]

    movie.source = movie.source or 'douban'
    logger.info(f"[Douban] Scraped: {movie.title} ({movie.year})")


if __name__ == "__main__":
    m = MovieInfo(title='盗梦空间')
    parse_data(m)
    print(m)
