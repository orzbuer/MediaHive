import os
import tempfile
import xml.etree.ElementTree as ET

import pytest

from core.datatype import MovieInfo
from core.nfo import generate_nfo


class TestNfoGeneration:
    def test_basic_nfo(self):
        movie = MovieInfo(
            title='Inception',
            original_title='Inception',
            year='2010',
            plot='A thief who steals corporate secrets.',
            director='Christopher Nolan',
            runtime='148',
            rating=8.8,
            votes=38000,
            genre=['Sci-Fi', 'Action', 'Thriller'],
            actor=['Leonardo DiCaprio', 'Joseph Gordon-Levitt'],
            country=['United States', 'United Kingdom'],
            tmdb_id='27205',
            imdb_id='tt1375666',
            cover='http://example.com/poster.jpg',
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            nfo_path = os.path.join(tmpdir, 'movie.nfo')
            generate_nfo(movie, nfo_path)

            assert os.path.exists(nfo_path)
            tree = ET.parse(nfo_path)
            root = tree.getroot()
            assert root.tag == 'movie'
            assert root.find('title').text == 'Inception'
            assert root.find('year').text == '2010'
            assert root.find('director').text == 'Christopher Nolan'
            assert len(root.findall('genre')) == 3
            assert len(root.findall('actor')) == 2
            assert root.find('.//uniqueid[@type="tmdb"]').text == '27205'
            assert root.find('.//uniqueid[@type="imdb"]').text == 'tt1375666'

    def test_minimal_nfo(self):
        movie = MovieInfo(title='Test Movie')
        with tempfile.TemporaryDirectory() as tmpdir:
            nfo_path = os.path.join(tmpdir, 'movie.nfo')
            generate_nfo(movie, nfo_path)

            tree = ET.parse(nfo_path)
            root = tree.getroot()
            assert root.find('title').text == 'Test Movie'

    def test_nfo_creates_directory(self):
        movie = MovieInfo(title='Test')
        with tempfile.TemporaryDirectory() as tmpdir:
            nfo_path = os.path.join(tmpdir, 'subdir', 'movie.nfo')
            generate_nfo(movie, nfo_path)
            assert os.path.exists(nfo_path)
