import unittest
import requests
from search_interface.api.search_api import SearchAPI
from search_interface.api.results_formatter import ResultsFormatter

class TestSearchE2E(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api_url = "https://website.com/api/search"
        cls.headers = {'Content-Type': 'application/json'}
        cls.sample_queries = [
            "python programming",
            "data science tutorials",
            "cloud infrastructure",
            "artificial intelligence",
            "machine learning applications",
        ]

    def test_search_query_basic(self):
        """Test a simple query with default parameters."""
        query = self.sample_queries[0]
        payload = {'query': query}
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        self.assertGreater(len(results), 0, "No results returned for basic query.")
        self.assertTrue(self._verify_relevance(results, query), "Results are not relevant.")

    def test_search_query_expansion(self):
        """Test query expansion results in more relevant data."""
        query = self.sample_queries[1]
        payload = {'query': query, 'expand_query': True}
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        self.assertGreater(len(results), 0, "No results returned for expanded query.")
        self.assertTrue(self._verify_relevance(results, query), "Irrelevant results found.")

    def test_search_query_no_results(self):
        """Test search query with no expected results."""
        query = "qwertyuioplkjhgfdsazxcvbnm"
        payload = {'query': query}
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        self.assertEqual(len(results), 0, "Results found for nonsensical query.")

    def test_search_query_edge_case_symbols(self):
        """Test query with symbols and edge cases."""
        query = "!@#$%^&*()<>?"
        payload = {'query': query}
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        self.assertEqual(len(results), 0, "Results found for edge case query.")

    def test_search_pagination(self):
        """Test search with pagination."""
        query = self.sample_queries[2]
        payload = {'query': query, 'page': 1, 'size': 10}
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        self.assertEqual(len(results), 10, "Pagination did not return the correct number of results.")
        self.assertTrue(self._verify_relevance(results, query), "Results are not relevant for paginated query.")

    def test_search_with_fuzzy_match(self):
        """Test fuzzy search for handling typos."""
        query = "dat scince"
        payload = {'query': query, 'fuzzy_match': True}
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        self.assertGreater(len(results), 0, "No results returned for fuzzy query.")
        self.assertTrue(self._verify_fuzzy_match(results), "Fuzzy match did not return correct results.")

    def test_search_boosting(self):
        """Test search with result boosting based on relevance feedback."""
        query = self.sample_queries[3]
        payload = {'query': query, 'boost_relevance': True}
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        self.assertGreater(len(results), 0, "No results returned for boosted query.")
        self.assertTrue(self._verify_relevance(results, query), "Boosted query did not improve relevance.")

    def test_search_query_phrases(self):
        """Test search using exact phrase match."""
        query = '"machine learning algorithms"'
        payload = {'query': query}
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        self.assertGreater(len(results), 0, "No results returned for phrase query.")
        self.assertTrue(self._verify_phrase_match(results, query), "Phrase query did not return accurate results.")

    def test_search_time_bound_query(self):
        """Test search with a time-bound query."""
        query = self.sample_queries[4]
        payload = {'query': query, 'time_range': 'last_30_days'}
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        self.assertGreater(len(results), 0, "No results returned for time-bound query.")
        self.assertTrue(self._verify_relevance(results, query), "Results are not relevant for time-bound query.")

    def test_search_result_format(self):
        """Test if the search result format adheres to the schema."""
        query = self.sample_queries[0]
        payload = {'query': query}
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        self.assertTrue(all(self._validate_result_format(res) for res in results), "Invalid result format.")

    def test_search_invalid_payload(self):
        """Test search with invalid payload."""
        payload = {'invalid_field': 'test'}
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 400, "Invalid payload did not return 400 status code.")

    @staticmethod
    def _validate_result_format(result):
        required_fields = ['title', 'url', 'snippet']
        return all(field in result for field in required_fields)

    @staticmethod
    def _verify_relevance(results, query):
        # Verify if the results are relevant based on the query keywords
        query_keywords = set(query.lower().split())
        for result in results:
            result_text = (result['title'] + " " + result.get('snippet', '')).lower()
            if not any(keyword in result_text for keyword in query_keywords):
                return False
        return True

    @staticmethod
    def _verify_fuzzy_match(results):
        # Verifies if fuzzy matching returned relevant results
        for result in results:
            title = result['title'].lower()
            if not any(term in title for term in ["data", "science"]):
                return False
        return True

    @staticmethod
    def _verify_phrase_match(results, query):
        # Verifies if the phrase match worked as expected.
        phrase = query.replace('"', '').lower()
        for result in results:
            if phrase not in result.get('snippet', '').lower():
                return False
        return True

if __name__ == "__main__":
    unittest.main()