import unittest
import requests
from flask import Flask, render_template
from search_interface.web_ui.app import app as search_app
from search_interface.api.search_api import search_query, format_results
from search_interface.web_ui.routes import search_results_page


class SearchInterfaceTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the test environment for all tests"""
        search_app.config['TESTING'] = True
        cls.client = search_app.test_client()

    def test_search_api_status(self):
        """Test if the search API is returning the correct status code"""
        response = self.client.get('/api/search?query=test')
        self.assertEqual(response.status_code, 200, "API should return status 200 for valid requests")

    def test_search_api_invalid_query(self):
        """Test search API with an invalid query"""
        response = self.client.get('/api/search?query=')
        self.assertEqual(response.status_code, 400, "API should return 400 for invalid queries")

    def test_search_api_results_format(self):
        """Test if the search API is returning the correct format for search results"""
        query = 'python'
        response = self.client.get(f'/api/search?query={query}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('results' in response.json, "Results key should be present in the response")
        self.assertIsInstance(response.json['results'], list, "Results should be a list")

    def test_search_results_empty(self):
        """Test search API with a query that returns no results"""
        response = self.client.get('/api/search?query=nonexistentterm')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['results'], [], "Results should be an empty list for non-existent terms")

    def test_search_api_special_characters(self):
        """Test search API with special characters in the query"""
        query = '!@#$%^&*()'
        response = self.client.get(f'/api/search?query={query}')
        self.assertEqual(response.status_code, 400, "API should handle special characters and return 400")

    def test_search_api_limit(self):
        """Test search API with a results limit"""
        response = self.client.get('/api/search?query=python&limit=5')
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.json['results']), 5, "API should limit the number of results")

    def test_search_ui_status(self):
        """Test if the search UI page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200, "Search UI should load correctly with status 200")

    def test_search_ui_results_display(self):
        """Test if the search UI displays search results correctly"""
        with self.client:
            response = self.client.get('/search?query=test')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Results for test', response.data, "Search UI should display results for the query")

    def test_search_ui_no_results(self):
        """Test if the search UI handles no results gracefully"""
        with self.client:
            response = self.client.get('/search?query=nonexistent')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'No results found', response.data, "UI should display no results message")

    def test_search_api_large_query(self):
        """Test search API with a very large query"""
        query = 'a' * 10000
        response = self.client.get(f'/api/search?query={query}')
        self.assertEqual(response.status_code, 400, "API should handle large queries and return 400")

    def test_search_api_pagination(self):
        """Test search API pagination"""
        response = self.client.get('/api/search?query=python&page=2')
        self.assertEqual(response.status_code, 200, "API should support pagination")
        self.assertIn('results', response.json, "Pagination response should include results")

    def test_search_ui_error_handling(self):
        """Test if the search UI handles API errors gracefully"""
        with self.client:
            response = self.client.get('/search?query=test')
            self.assertEqual(response.status_code, 200, "UI should load even when the API returns errors")
            self.assertIn(b'Something went wrong', response.data, "UI should display error messages")

    def test_search_api_method_not_allowed(self):
        """Test API response for methods not allowed"""
        response = self.client.post('/api/search?query=test')
        self.assertEqual(response.status_code, 405, "API should return 405 for unsupported methods")

    def test_search_results_relevance(self):
        """Test if the search API returns relevant results based on ranking"""
        query = 'python programming'
        response = self.client.get(f'/api/search?query={query}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json['results']) > 0, "Search results should not be empty for relevant queries")

    def test_search_ui_template_rendering(self):
        """Test if search templates are rendered properly"""
        with search_app.test_request_context('/search?query=python'):
            rendered_html = render_template('results.html', query='python', results=[])
            self.assertIn('Results for python', rendered_html, "Results page should render with query term")

    def test_api_rate_limiting(self):
        """Test if API enforces rate limiting"""
        for _ in range(100):
            response = self.client.get('/api/search?query=test')
        self.assertEqual(response.status_code, 429, "API should enforce rate limiting after multiple requests")

    def test_ui_css_load(self):
        """Test if the main CSS file loads in the search UI"""
        response = self.client.get('/static/styles.css')
        self.assertEqual(response.status_code, 200, "CSS should load correctly with status 200")

    def test_ui_javascript_load(self):
        """Test if the main JavaScript file loads in the search UI"""
        response = self.client.get('/static/script.js')
        self.assertEqual(response.status_code, 200, "JavaScript should load correctly with status 200")

    def test_ui_cross_origin_resource_sharing(self):
        """Test if UI implements CORS headers correctly"""
        response = self.client.get('/')
        self.assertIn('Access-Control-Allow-Origin', response.headers, "CORS headers should be present in UI")

    def test_search_results_empty_page(self):
        """Test UI behavior when searching with no query"""
        response = self.client.get('/search?query=')
        self.assertIn(b'Please enter a search term', response.data, "UI should prompt users to enter a query")

if __name__ == '__main__':
    unittest.main()