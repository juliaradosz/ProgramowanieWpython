from unittest.mock import MagicMock, patch

from app.utils import fetch_books_by_query, fetch_books_by_subject


def _mock_search_response(docs):
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {'docs': docs}
    return resp


def _mock_subject_response(works):
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {'works': works}
    return resp


SAMPLE_DOC = {
    'title': 'The Hobbit',
    'author_name': ['J.R.R. Tolkien'],
    'cover_i': 12345,
    'first_publish_year': 1937,
    'subject': ['Fantasy'],
    'publisher': ['Houghton Mifflin'],
    'key': '/works/OL12345W',
    'first_sentence': ['In a hole in the ground there lived a hobbit.'],
    'number_of_pages_median': 310,
}


class TestFetchBooksByQuery:
    def test_returns_list_of_results(self):
        with patch('app.utils.requests.get', return_value=_mock_search_response([SAMPLE_DOC])):
            results = fetch_books_by_query('hobbit')
        assert len(results) == 1

    def test_each_result_has_expected_keys(self):
        with patch('app.utils.requests.get', return_value=_mock_search_response([SAMPLE_DOC])):
            results = fetch_books_by_query('hobbit')
        expected = {'title', 'author', 'cover_url', 'google_id', 'year', 'genre', 'description'}
        assert expected.issubset(results[0].keys())

    def test_empty_docs_return_empty_list(self):
        with patch('app.utils.requests.get', return_value=_mock_search_response([])):
            results = fetch_books_by_query('nic')
        assert results == []

    def test_docs_without_cover_are_skipped(self):
        doc = {**SAMPLE_DOC, 'cover_i': None}
        with patch('app.utils.requests.get', return_value=_mock_search_response([doc])):
            results = fetch_books_by_query('hobbit')
        assert results == []

    def test_max_two_books_per_author(self):
        docs = [
            {**SAMPLE_DOC, 'title': f'Book {i}', 'key': f'/works/OL{i}W', 'cover_i': 100 + i}
            for i in range(5)
        ]
        with patch('app.utils.requests.get', return_value=_mock_search_response(docs)):
            results = fetch_books_by_query('tolkien')
        assert len(results) == 2

    def test_boring_titles_filtered(self):
        doc = {**SAMPLE_DOC, 'title': 'Tolkien Encyclopedia'}
        with patch('app.utils.requests.get', return_value=_mock_search_response([doc])):
            results = fetch_books_by_query('tolkien')
        assert results == []

    def test_network_error_returns_empty_list(self):
        with patch('app.utils.requests.get', side_effect=Exception('network down')):
            results = fetch_books_by_query('whatever')
        assert results == []


class TestFetchBooksBySubject:
    @staticmethod
    def _make_work(**overrides):
        base = {
            'title': 'The Hobbit',
            'authors': [{'name': 'Tolkien'}],
            'cover_id': 12345,
            'first_publish_year': 1937,
            'key': '/works/OL1W',
        }
        base.update(overrides)
        return base

    def test_returns_list_of_results(self):
        work = self._make_work()
        with patch('app.utils.requests.get', return_value=_mock_subject_response([work])):
            results = fetch_books_by_subject('fantasy_fiction')
        assert len(results) == 1
        assert results[0]['title'] == 'The Hobbit'

    def test_works_without_authors_skipped(self):
        work = self._make_work(authors=[])
        with patch('app.utils.requests.get', return_value=_mock_subject_response([work])):
            results = fetch_books_by_subject('fantasy_fiction')
        assert results == []

    def test_works_without_cover_skipped(self):
        work = self._make_work(cover_id=None, cover_edition_key=None)
        with patch('app.utils.requests.get', return_value=_mock_subject_response([work])):
            results = fetch_books_by_subject('fantasy_fiction')
        assert results == []

    def test_empty_works_returns_empty_list(self):
        with patch('app.utils.requests.get', return_value=_mock_subject_response([])):
            results = fetch_books_by_subject('fantasy_fiction')
        assert results == []

    def test_network_error_returns_empty_list(self):
        with patch('app.utils.requests.get', side_effect=Exception('down')):
            results = fetch_books_by_subject('fantasy_fiction')
        assert results == []
