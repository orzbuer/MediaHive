import pytest
from core.scanner import guess_title_and_year


class TestGuessTitle:
    def test_simple_title_with_year_parens(self):
        title, year = guess_title_and_year('Inception (2010).mkv')
        assert title == 'Inception'
        assert year == '2010'

    def test_dotted_filename(self):
        title, year = guess_title_and_year('The.Dark.Knight.2008.1080p.BluRay.x264.mkv')
        assert title == 'The Dark Knight'
        assert year == '2008'

    def test_brackets_year(self):
        title, year = guess_title_and_year('Parasite [2019] HDRip.mp4')
        assert title == 'Parasite'
        assert year == '2019'

    def test_chinese_title(self):
        title, year = guess_title_and_year('盗梦空间 (2010).mkv')
        assert title == '盗梦空间'
        assert year == '2010'

    def test_no_year(self):
        title, year = guess_title_and_year('Some Random Movie.mp4')
        assert title == 'Some Random Movie'
        assert year is None

    def test_quality_tags_removed(self):
        title, year = guess_title_and_year('Movie.Name.2020.BluRay.REMUX.x265.DTS.mkv')
        assert title == 'Movie Name'
        assert year == '2020'

    def test_hyphenated_title(self):
        title, year = guess_title_and_year('Spider-Man.No.Way.Home.2021.WEB-DL.mp4')
        assert title == 'Spider Man No Way Home'
        assert year == '2021'

    def test_ignore_words(self):
        title, year = guess_title_and_year('Movie.Name.2020.1080P.BluRay.mkv')
        assert '1080P' not in (title or '')
        assert year == '2020'
