import unittest
from unittest.mock import patch, MagicMock
from crawler_manager import CrawlerManager
from page_fetcher import PageFetcher
from content_extractor import ContentExtractor
from robots_parser import RobotsParser
from crawler_policies.politeness_policy import PolitenessPolicy

class CrawlerTests(unittest.TestCase):

    @patch('page_fetcher.PageFetcher.fetch')
    def test_fetch_page_success(self, mock_fetch):
        """Test successful fetching of a page."""
        mock_fetch.return_value = '<html><body>Test Page</body></html>'
        fetcher = PageFetcher()
        content = fetcher.fetch('http://website.com')
        self.assertEqual(content, '<html><body>Test Page</body></html>')

    @patch('page_fetcher.PageFetcher.fetch')
    def test_fetch_page_failure(self, mock_fetch):
        """Test fetching a page that results in a failure."""
        mock_fetch.side_effect = Exception("Failed to fetch page")
        fetcher = PageFetcher()
        with self.assertRaises(Exception) as context:
            fetcher.fetch('http://website.com')
        self.assertTrue("Failed to fetch page" in str(context.exception))

    @patch('content_extractor.ContentExtractor.extract')
    def test_extract_content(self, mock_extract):
        """Test content extraction from a web page."""
        mock_extract.return_value = "Test Page Content"
        extractor = ContentExtractor()
        content = extractor.extract('<html><body>Test Page</body></html>')
        self.assertEqual(content, "Test Page Content")

    def test_extract_empty_page(self):
        """Test content extraction from an empty page."""
        extractor = ContentExtractor()
        content = extractor.extract('')
        self.assertEqual(content, '')

    def test_politeness_policy_respected(self):
        """Test that the politeness policy is respected between requests."""
        policy = PolitenessPolicy(min_delay=2)
        last_request_time = policy.last_request_time
        can_fetch = policy.can_fetch()
        self.assertTrue(can_fetch)
        self.assertNotEqual(last_request_time, policy.last_request_time)

    def test_politeness_policy_not_respected(self):
        """Test that politeness policy prevents too frequent requests."""
        policy = PolitenessPolicy(min_delay=5)
        policy.update_last_request_time()
        can_fetch = policy.can_fetch()
        self.assertFalse(can_fetch)

    @patch('robots_parser.RobotsParser.allowed')
    def test_robots_allowed(self, mock_allowed):
        """Test that a URL is allowed based on robots.txt."""
        mock_allowed.return_value = True
        parser = RobotsParser()
        self.assertTrue(parser.allowed('http://website.com/page'))

    @patch('robots_parser.RobotsParser.allowed')
    def test_robots_disallowed(self, mock_allowed):
        """Test that a URL is disallowed based on robots.txt."""
        mock_allowed.return_value = False
        parser = RobotsParser()
        self.assertFalse(parser.allowed('http://website.com/blocked'))

    def test_crawl_single_page(self):
        """Test crawling a single page and extracting its content."""
        manager = CrawlerManager()
        manager.fetch_page = MagicMock(return_value='<html><body>Test Page</body></html>')
        manager.extract_content = MagicMock(return_value='Test Page Content')
        
        url = 'http://website.com'
        content = manager.crawl_page(url)
        
        manager.fetch_page.assert_called_once_with(url)
        manager.extract_content.assert_called_once_with('<html><body>Test Page</body></html>')
        self.assertEqual(content, 'Test Page Content')

    def test_crawl_page_queue(self):
        """Test crawling multiple pages from a queue."""
        manager = CrawlerManager()
        manager.page_queue = ['http://website.com/page1', 'http://website.com/page2']
        manager.fetch_page = MagicMock(side_effect=['<html>Page 1</html>', '<html>Page 2</html>'])
        manager.extract_content = MagicMock(side_effect=['Content 1', 'Content 2'])
        
        manager.crawl_queue()
        
        manager.fetch_page.assert_any_call('http://website.com/page1')
        manager.fetch_page.assert_any_call('http://website.com/page2')
        self.assertEqual(manager.extract_content.call_count, 2)

    @patch('crawler_policies.PolitenessPolicy.can_fetch')
    def test_crawler_respects_politeness(self, mock_can_fetch):
        """Test that the crawler respects politeness policy."""
        mock_can_fetch.return_value = True
        manager = CrawlerManager()
        manager.page_queue = ['http://website.com/page1']
        manager.fetch_page = MagicMock(return_value='<html>Page 1</html>')
        manager.extract_content = MagicMock(return_value='Content 1')
        
        manager.crawl_queue()
        self.assertTrue(manager.fetch_page.called)

    @patch('crawler_policies.PolitenessPolicy.can_fetch')
    def test_crawler_blocked_by_politeness(self, mock_can_fetch):
        """Test that the crawler stops when politeness policy blocks fetching."""
        mock_can_fetch.return_value = False
        manager = CrawlerManager()
        manager.page_queue = ['http://website.com/page1']
        manager.fetch_page = MagicMock()
        
        manager.crawl_queue()
        self.assertFalse(manager.fetch_page.called)

    @patch('crawler_manager.CrawlerManager.crawl_queue')
    def test_crawl_manager_full_run(self, mock_crawl_queue):
        """Test the full run of the crawler manager."""
        manager = CrawlerManager()
        manager.run_crawler()
        self.assertTrue(mock_crawl_queue.called)

    def test_empty_page_queue(self):
        """Test the behavior when the page queue is empty."""
        manager = CrawlerManager()
        manager.page_queue = []
        manager.fetch_page = MagicMock()
        
        manager.crawl_queue()
        self.assertFalse(manager.fetch_page.called)

    def test_update_page_queue(self):
        """Test updating the page queue."""
        manager = CrawlerManager()
        urls = ['http://website.com/page1', 'http://website.com/page2']
        manager.update_page_queue(urls)
        self.assertEqual(manager.page_queue, urls)

    def test_page_queue_empty_on_update(self):
        """Test that updating the queue with empty data results in an empty queue."""
        manager = CrawlerManager()
        manager.update_page_queue([])
        self.assertEqual(manager.page_queue, [])

if __name__ == '__main__':
    unittest.main()