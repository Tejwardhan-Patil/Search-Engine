import unittest
from unittest.mock import patch, MagicMock
from crawler.crawler_manager import CrawlerManager
from crawler.page_fetcher import PageFetcher
from crawler.content_extractor import ContentExtractor
from crawler.robots_parser import RobotsParser
from crawler.crawler_policies.politeness_policy import PolitenessPolicy

class TestCrawlerManager(unittest.TestCase):

    @patch('crawler.page_fetcher.PageFetcher')
    @patch('crawler.content_extractor.ContentExtractor')
    @patch('crawler.robots_parser.RobotsParser')
    @patch('crawler.crawler_policies.politeness_policy.PolitenessPolicy')
    def setUp(self, MockPolitenessPolicy, MockRobotsParser, MockContentExtractor, MockPageFetcher):
        # Create mock instances
        self.mock_fetcher = MockPageFetcher.return_value
        self.mock_extractor = MockContentExtractor.return_value
        self.mock_robots_parser = MockRobotsParser.return_value
        self.mock_policy = MockPolitenessPolicy.return_value

        # Initialize CrawlerManager with mocks
        self.manager = CrawlerManager(
            fetcher=self.mock_fetcher,
            extractor=self.mock_extractor,
            robots_parser=self.mock_robots_parser,
            policy=self.mock_policy
        )

    def test_initialize_crawler(self):
        # Test initializing crawler with required components
        self.assertIsInstance(self.manager.fetcher, PageFetcher)
        self.assertIsInstance(self.manager.extractor, ContentExtractor)
        self.assertIsInstance(self.manager.robots_parser, RobotsParser)
        self.assertIsInstance(self.manager.policy, PolitenessPolicy)

    def test_add_url_to_queue(self):
        # Test adding a URL to the crawling queue
        url = "https://website.com"
        self.manager.add_url(url)
        self.mock_policy.apply_politeness.assert_called_once_with(url)
        self.assertIn(url, self.manager.url_queue)

    def test_fetch_page_success(self):
        # Test successful page fetching
        url = "https://website.com"
        self.mock_fetcher.fetch_page.return_value = "<html>Some content</html>"
        
        content = self.manager.fetch_page(url)
        self.mock_fetcher.fetch_page.assert_called_with(url)
        self.assertEqual(content, "<html>Some content</html>")

    def test_fetch_page_failure(self):
        # Test fetching page failure scenario
        url = "https://invalid-website.com"
        self.mock_fetcher.fetch_page.return_value = None
        
        content = self.manager.fetch_page(url)
        self.mock_fetcher.fetch_page.assert_called_with(url)
        self.assertIsNone(content)

    def test_process_fetched_content(self):
        # Test extracting content from fetched HTML
        html = "<html><body>Text</body></html>"
        self.mock_extractor.extract_content.return_value = "Text"
        
        extracted_content = self.manager.process_fetched_content(html)
        self.mock_extractor.extract_content.assert_called_with(html)
        self.assertEqual(extracted_content, "Text")

    @patch('crawler_manager.CrawlerManager.fetch_page')
    @patch('crawler_manager.CrawlerManager.process_fetched_content')
    def test_crawl_url(self, mock_process_fetched_content, mock_fetch_page):
        # Test crawling a single URL
        url = "https://website.com"
        mock_fetch_page.return_value = "<html>Content</html>"
        mock_process_fetched_content.return_value = "Processed content"

        result = self.manager.crawl_url(url)
        self.assertTrue(result)
        mock_fetch_page.assert_called_once_with(url)
        mock_process_fetched_content.assert_called_once_with("<html>Content</html>")

    @patch('crawler_manager.CrawlerManager.crawl_url')
    def test_crawl_multiple_urls(self, mock_crawl_url):
        # Test crawling multiple URLs in sequence
        urls = ["https://website.com", "https://anotherwebsite.com"]
        self.manager.url_queue.extend(urls)

        mock_crawl_url.side_effect = [True, True]
        self.manager.crawl()
        self.assertEqual(mock_crawl_url.call_count, 2)

    @patch('crawler_manager.CrawlerManager.crawl_url')
    def test_crawl_multiple_urls_with_failures(self, mock_crawl_url):
        # Test crawling multiple URLs, with some failures
        urls = ["https://website.com", "https://brokenwebsite.com", "https://website2.com"]
        self.manager.url_queue.extend(urls)

        mock_crawl_url.side_effect = [True, False, True]
        self.manager.crawl()
        self.assertEqual(mock_crawl_url.call_count, 3)

    def test_apply_politeness_policy(self):
        # Test if politeness policy is applied correctly
        url = "https://website.com"
        self.manager.add_url(url)
        self.mock_policy.apply_politeness.assert_called_with(url)

    @patch('time.sleep', return_value=None)
    def test_crawler_respects_delay_between_requests(self, mock_sleep):
        # Test that the crawler respects politeness delays
        url = "https://website.com"
        self.manager.add_url(url)
        
        self.manager.crawl()
        self.mock_policy.apply_politeness.assert_called_with(url)
        mock_sleep.assert_called_once()

    def test_handle_robots_txt(self):
        # Test if robots.txt rules are respected
        url = "https://website.com"
        self.mock_robots_parser.is_allowed.return_value = False
        
        result = self.manager.is_allowed_to_crawl(url)
        self.mock_robots_parser.is_allowed.assert_called_with(url)
        self.assertFalse(result)

    def test_crawl_skipped_due_to_robots_txt(self):
        # Test crawling skips URLs disallowed by robots.txt
        url = "https://disallowed-website.com"
        self.mock_robots_parser.is_allowed.return_value = False
        
        result = self.manager.crawl_url(url)
        self.assertFalse(result)
        self.mock_fetcher.fetch_page.assert_not_called()

    def test_crawl_obeys_robots_txt(self):
        # Test crawling proceeds if robots.txt allows
        url = "https://allowed-website.com"
        self.mock_robots_parser.is_allowed.return_value = True
        self.mock_fetcher.fetch_page.return_value = "<html>Content</html>"

        result = self.manager.crawl_url(url)
        self.assertTrue(result)
        self.mock_fetcher.fetch_page.assert_called_with(url)

    def test_process_empty_url_queue(self):
        # Test handling empty URL queue
        self.manager.url_queue = []
        with self.assertLogs('crawler_manager', level='INFO') as cm:
            self.manager.crawl()
        self.assertIn('No URLs to crawl', cm.output[0])

    def test_crawler_shuts_down_gracefully(self):
        # Test if crawler shuts down without errors after crawling all URLs
        urls = ["https://website1.com", "https://website2.com"]
        self.manager.url_queue.extend(urls)

        with patch('crawler_manager.CrawlerManager.crawl_url', return_value=True):
            self.manager.crawl()
        self.assertEqual(self.manager.url_queue, [])

if __name__ == '__main__':
    unittest.main()