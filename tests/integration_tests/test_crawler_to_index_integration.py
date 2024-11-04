import unittest
import time
import subprocess
from crawler.crawler_manager import CrawlerManager
from crawler.content_extractor import ContentExtractor

class TestCrawlerToIndexIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.crawler_manager = CrawlerManager()
        cls.content_extractor = ContentExtractor()
        cls.crawl_data = []

    def test_crawl_to_index_flow(self):
        """Test the end-to-end flow from crawling to indexing"""

        # Start the crawling process
        self.start_crawling()

        # Verify crawled data is fetched
        self.verify_crawled_data()

        # Extract content from crawled pages
        self.extract_content()

        # Build the index using subprocess for Java components
        self.build_index_with_subprocess()

        # Verify the index was created successfully
        self.verify_index_with_subprocess()

    def start_crawling(self):
        """Initiate the crawling process"""
        urls_to_crawl = [
            "https://website.com/page1",
            "https://website.com/page2",
            "https://website.com/page3"
        ]
        
        self.crawler_manager.add_urls(urls_to_crawl)
        self.crawler_manager.start_crawl()
        
        time.sleep(2) 

        crawled_urls = self.crawler_manager.get_crawled_urls()
        self.assertTrue(len(crawled_urls) > 0, "Crawling should fetch URLs")
        self.crawl_data = crawled_urls

    def verify_crawled_data(self):
        """Check that crawled data contains the expected URLs"""
        expected_urls = [
            "https://website.com/page1",
            "https://website.com/page2",
            "https://website.com/page3"
        ]
        
        for url in expected_urls:
            self.assertIn(url, self.crawl_data, f"{url} should be in crawled data")

    def extract_content(self):
        """Extract content from the crawled pages"""
        self.documents = {}
        for url in self.crawl_data:
            page_content = self.crawler_manager.get_page_content(url)
            extracted_content = self.content_extractor.extract(page_content)
            
            self.assertIsNotNone(extracted_content, "Extracted content should not be None")
            self.assertGreater(len(extracted_content), 0, "Content should not be empty")
            self.documents[url] = extracted_content

    def build_index_with_subprocess(self):
        """Build the index using Java subprocess"""
        # Prepare input for the index builder (in a file)
        with open('crawled_documents.txt', 'w') as f:
            for url, content in self.documents.items():
                f.write(f'{url}\n{content}\n')

        # Call the Java inverted_index_builder using subprocess
        build_index_cmd = ['java', 'indexing.inverted_index.inverted_index_builder', 'crawled_documents.txt']
        subprocess.run(build_index_cmd, check=True)

    def verify_index_with_subprocess(self):
        """Verify the index using Java subprocess"""
        # Load the index using the Java IndexFileManager subprocess
        load_index_cmd = ['java', 'indexing.index_storage.IndexFileManager', 'load']
        result = subprocess.run(load_index_cmd, capture_output=True, text=True, check=True)

        # Verify the index output
        index_output = result.stdout
        self.assertGreater(len(index_output), 0, "Index should have entries")
        for url in self.crawl_data:
            self.assertIn(url, index_output, f"{url} should be indexed")

    def test_reindexing_after_crawl(self):
        """Test re-indexing after new crawl data"""
        new_urls = ["https://website.com/page4", "https://website.com/page5"]

        # Crawl new URLs
        self.crawler_manager.add_urls(new_urls)
        self.crawler_manager.start_crawl()
        
        time.sleep(2) 

        crawled_urls = self.crawler_manager.get_crawled_urls()
        self.assertTrue(len(crawled_urls) > 3, "New URLs should be added to crawled data")

        # Extract content and re-index using subprocess
        new_documents = {}
        for url in new_urls:
            content = self.crawler_manager.get_page_content(url)
            extracted_content = self.content_extractor.extract(content)
            new_documents[url] = extracted_content

        with open('new_crawled_documents.txt', 'w') as f:
            for url, content in new_documents.items():
                f.write(f'{url}\n{content}\n')

        build_index_cmd = ['java', 'indexing.inverted_index.inverted_index_builder', 'new_crawled_documents.txt']
        subprocess.run(build_index_cmd, check=True)

        # Verify the updated index contains new URLs
        load_index_cmd = ['java', 'indexing.index_storage.IndexFileManager', 'load']
        result = subprocess.run(load_index_cmd, capture_output=True, text=True, check=True)

        updated_index = result.stdout
        self.assertIn("https://website.com/page4", updated_index, "New URLs should be indexed")
        self.assertIn("https://website.com/page5", updated_index, "New URLs should be indexed")

    def test_indexing_empty_crawl(self):
        """Ensure index is not created if no data was crawled"""
        empty_urls = []
        self.crawler_manager.add_urls(empty_urls)
        self.crawler_manager.start_crawl()

        time.sleep(1)

        crawled_urls = self.crawler_manager.get_crawled_urls()
        self.assertEqual(len(crawled_urls), 0, "No URLs should be crawled")

        # Attempt to build the index with no data
        with open('empty_crawled_documents.txt', 'w') as f:
            f.write('')

        build_index_cmd = ['java', 'indexing.inverted_index.inverted_index_builder', 'empty_crawled_documents.txt']
        subprocess.run(build_index_cmd, check=True)

        load_index_cmd = ['java', 'indexing.index_storage.IndexFileManager', 'load']
        result = subprocess.run(load_index_cmd, capture_output=True, text=True, check=True)

        index = result.stdout
        self.assertEqual(len(index), 0, "Index should remain empty with no crawled data")

    def test_inconsistent_crawl_data(self):
        """Test behavior with inconsistent or incomplete crawl data"""
        inconsistent_urls = ["https://website.com/page6"]
        self.crawler_manager.add_urls(inconsistent_urls)

        # Simulate a crawl with incomplete data
        def mock_fetch_page(url):
            if url == "https://website.com/page6":
                return None  # Simulate a failure to fetch this page
            return "<html>Valid content</html>"

        self.crawler_manager.get_page_content = mock_fetch_page
        self.crawler_manager.start_crawl()

        time.sleep(1)

        crawled_urls = self.crawler_manager.get_crawled_urls()
        self.assertIn("https://website.com/page6", crawled_urls, "Incomplete URL should be in the crawled list")

        # Ensure the index skips the failed content
        with open('inconsistent_crawled_documents.txt', 'w') as f:
            for url in crawled_urls:
                if url != "https://website.com/page6":
                    f.write(f'{url}\nValid content\n')

        build_index_cmd = ['java', 'indexing.inverted_index.inverted_index_builder', 'inconsistent_crawled_documents.txt']
        subprocess.run(build_index_cmd, check=True)

        load_index_cmd = ['java', 'indexing.index_storage.IndexFileManager', 'load']
        result = subprocess.run(load_index_cmd, capture_output=True, text=True, check=True)

        index = result.stdout
        self.assertNotIn("https://website.com/page6", index, "Failed pages should not be indexed")

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        cls.crawler_manager.clear_queue()
        subprocess.run(['java', 'indexing.index_storage.IndexFileManager', 'clear'], check=True)


if __name__ == "__main__":
    unittest.main()