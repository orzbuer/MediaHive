import pytest
from core.datatype import MovieInfo


class TestMovieInfo:
    def test_merge_fills_empty_fields(self):
        m1 = MovieInfo(title='Inception', year='2010')
        m2 = MovieInfo(director='Christopher Nolan', rating=8.8, genre=['Sci-Fi'])
        m1.merge(m2)
        assert m1.title == 'Inception'
        assert m1.director == 'Christopher Nolan'
        assert m1.rating == 8.8
        assert m1.genre == ['Sci-Fi']

    def test_merge_does_not_overwrite(self):
        m1 = MovieInfo(title='Inception', director='Nolan')
        m2 = MovieInfo(title='Wrong Title', director='Wrong')
        m1.merge(m2)
        assert m1.title == 'Inception'
        assert m1.director == 'Nolan'

    def test_merge_ignores_none_and_empty(self):
        m1 = MovieInfo(title='Inception')
        m2 = MovieInfo(title=None, genre=[], director='')
        m1.merge(m2)
        assert m1.title == 'Inception'
        assert m1.genre == []

    def test_has_required_keys(self):
        m = MovieInfo(title='Inception', cover='http://example.com/poster.jpg')
        assert m.has_required_keys(['title', 'cover'])
        assert not m.has_required_keys(['title', 'cover', 'director'])

    def test_has_required_keys_empty_list(self):
        m = MovieInfo(title='Test', genre=[])
        assert not m.has_required_keys(['genre'])

    def test_str_representation(self):
        m = MovieInfo(title='Inception', year='2010')
        s = str(m)
        assert 'Inception' in s
        assert '2010' in s
