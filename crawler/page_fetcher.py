import requests
from urllib.parse import urlparse, urljoin
import time
from requests.exceptions import RequestException, Timeout, TooManyRedirects
from urllib.robotparser import RobotFileParser
import logging
import concurrent.futures

# Logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('PageFetcher')

class PageFetcher:
    def __init__(self, user_agent: str, timeout: int = 10, max_retries: int = 3):
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries
        self.visited_urls = set()
        self.robots_cache = {}

    def fetch(self, url: str) -> str:
        """
        Fetches a web page from a URL, handling errors and retries.
        :param url: The URL to fetch.
        :return: The content of the page if successful, None otherwise.
        """
        if not self.is_allowed_by_robots(url):
            logger.info(f"Blocked by robots.txt: {url}")
            return None

        attempt = 0
        while attempt < self.max_retries:
            try:
                headers = {'User-Agent': self.user_agent}
                response = requests.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                logger.info(f"Successfully fetched: {url}")
                return response.text
            except (RequestException, Timeout, TooManyRedirects) as e:
                logger.error(f"Error fetching {url}: {e}")
                attempt += 1
                time.sleep(2 ** attempt)  # Exponential backoff
        return None

    def is_allowed_by_robots(self, url: str) -> bool:
        """
        Checks if a URL is allowed to be crawled by robots.txt.
        :param url: The URL to check.
        :return: True if the URL is allowed, False otherwise.
        """
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        if base_url in self.robots_cache:
            rp = self.robots_cache[base_url]
        else:
            rp = RobotFileParser()
            try:
                rp.set_url(base_url)
                rp.read()
                self.robots_cache[base_url] = rp
            except Exception as e:
                logger.error(f"Failed to parse robots.txt for {base_url}: {e}")
                return True  # If robots.txt cannot be fetched, assume it's allowed

        return rp.can_fetch(self.user_agent, url)

    def fetch_pages_concurrently(self, urls: list) -> dict:
        """
        Fetches multiple pages concurrently using thread pool.
        :param urls: List of URLs to fetch.
        :return: A dictionary with URLs as keys and page content (or None) as values.
        """
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(self.fetch, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results[url] = result
                except Exception as e:
                    logger.error(f"Error fetching {url} concurrently: {e}")
                    results[url] = None
        return results

    def is_html(self, url: str) -> bool:
        """
        Checks if the fetched content type is HTML.
        :param url: The URL to check.
        :return: True if the content is HTML, False otherwise.
        """
        try:
            response = requests.head(url, headers={'User-Agent': self.user_agent}, timeout=self.timeout)
            content_type = response.headers.get('Content-Type', '')
            return 'text/html' in content_type
        except RequestException as e:
            logger.error(f"Failed to determine content type for {url}: {e}")
            return False

    def normalize_url(self, base_url: str, link: str) -> str:
        """
        Normalizes relative URLs to absolute URLs.
        :param base_url: The base URL to resolve relative URLs.
        :param link: The URL to normalize.
        :return: A normalized absolute URL.
        """
        return urljoin(base_url, link)

    def add_visited(self, url: str) -> None:
        """
        Adds a URL to the set of visited URLs.
        :param url: The URL to add.
        """
        self.visited_urls.add(url)

    def has_visited(self, url: str) -> bool:
        """
        Checks if a URL has already been visited.
        :param url: The URL to check.
        :return: True if the URL has been visited, False otherwise.
        """
        return url in self.visited_urls

    def fetch_with_retry(self, url: str, retry_count: int = 3) -> str:
        """
        Fetches a page with retries in case of failures.
        :param url: The URL to fetch.
        :param retry_count: Number of retries in case of failures.
        :return: Page content or None if all retries fail.
        """
        for attempt in range(retry_count):
            try:
                return self.fetch(url)
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {url}: {e}")
                time.sleep(2 ** attempt)
        return None

    def extract_links(self, page_content: str) -> list:
        """
        Extracts all anchor (<a>) tag links from the page content.
        :param page_content: The HTML content of the page.
        :return: A list of extracted URLs.
        """
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(page_content, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        return links

    def crawl(self, start_url: str, max_depth: int = 3) -> None:
        """
        Crawls a website starting from the start_url, up to a specified depth.
        :param start_url: The URL to start crawling from.
        :param max_depth: Maximum depth to crawl.
        """
        urls_to_visit = [(start_url, 0)]
        while urls_to_visit:
            current_url, depth = urls_to_visit.pop(0)
            if depth > max_depth or self.has_visited(current_url):
                continue

            page_content = self.fetch(current_url)
            if page_content is None:
                continue

            logger.info(f"Crawling {current_url}, Depth: {depth}")
            self.add_visited(current_url)

            links = self.extract_links(page_content)
            for link in links:
                absolute_link = self.normalize_url(current_url, link)
                if absolute_link not in self.visited_urls:
                    urls_to_visit.append((absolute_link, depth + 1))


if __name__ == "__main__":
    fetcher = PageFetcher(user_agent="SearchEngineBot/1.0")
    start_url = "https://website.com"
    fetcher.crawl(start_url)