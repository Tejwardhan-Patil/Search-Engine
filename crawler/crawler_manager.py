import threading
import time
from queue import Queue
from page_fetcher import PageFetcher
from content_extractor import ContentExtractor
from robots_parser import RobotsParser
from crawler_policies.politeness_policy import PolitenessPolicy

class CrawlerManager:
    def __init__(self, start_urls, max_workers=10, politeness_delay=2):
        self.url_queue = Queue()
        self.crawled_urls = set()
        self.start_urls = start_urls
        self.max_workers = max_workers
        self.politeness_policy = PolitenessPolicy(politeness_delay)
        self.page_fetcher = PageFetcher()
        self.content_extractor = ContentExtractor()
        self.robots_parser = RobotsParser()
        self.lock = threading.Lock()
        
        for url in start_urls:
            self.url_queue.put(url)

    def can_crawl(self, url):
        robots_txt = self.robots_parser.parse(url)
        if robots_txt and not robots_txt.allowed(url):
            return False
        return True

    def worker(self):
        while not self.url_queue.empty():
            url = self.url_queue.get()

            # Respect politeness policy
            self.politeness_policy.enforce(url)

            if self.can_crawl(url):
                try:
                    self.crawl(url)
                except Exception as e:
                    print(f"Error crawling {url}: {e}")
            self.url_queue.task_done()

    def crawl(self, url):
        # Fetch the page
        page_content = self.page_fetcher.fetch(url)
        
        if page_content:
            # Extract data from the page
            extracted_data = self.content_extractor.extract(page_content)

            with self.lock:
                if url not in self.crawled_urls:
                    self.crawled_urls.add(url)
                    print(f"Crawled: {url}")
            
            # Add more URLs to the queue if new links found
            new_urls = extracted_data.get('links', [])
            for new_url in new_urls:
                with self.lock:
                    if new_url not in self.crawled_urls:
                        self.url_queue.put(new_url)

    def start_crawl(self):
        threads = []
        for _ in range(self.max_workers):
            thread = threading.Thread(target=self.worker)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        print("Crawling complete.")

# Usage
if __name__ == "__main__":
    start_urls = ["https://website.com"]
    crawler_manager = CrawlerManager(start_urls, max_workers=5, politeness_delay=1)
    crawler_manager.start_crawl()