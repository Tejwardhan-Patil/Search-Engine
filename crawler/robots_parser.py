import re
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
import time

class RobotsParser:
    def __init__(self, user_agent="*"):
        self.user_agent = user_agent
        self.rules = {}
        self.sitemaps = []
        self.crawl_delay = None

    def fetch_robots(self, base_url):
        parsed_url = urlparse(base_url)
        robots_url = urljoin(base_url, "/robots.txt")
        try:
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 200:
                self.parse_robots(response.text)
            else:
                print(f"Robots.txt not found at {robots_url}, status: {response.status_code}")
        except requests.RequestException as e:
            print(f"Failed to fetch robots.txt: {e}")

    def parse_robots(self, robots_text):
        current_user_agent = None
        for line in robots_text.splitlines():
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            if line.lower().startswith('user-agent:'):
                current_user_agent = line.split(':')[1].strip()
            elif current_user_agent and (self.user_agent == '*' or current_user_agent == self.user_agent):
                self._parse_rule(line)
            elif line.lower().startswith('sitemap:'):
                self.sitemaps.append(line.split(':', 1)[1].strip())

    def _parse_rule(self, line):
        if line.lower().startswith('disallow:'):
            path = line.split(':', 1)[1].strip()
            if path:
                if 'disallow' not in self.rules:
                    self.rules['disallow'] = []
                self.rules['disallow'].append(re.escape(path))
        elif line.lower().startswith('allow:'):
            path = line.split(':', 1)[1].strip()
            if path:
                if 'allow' not in self.rules:
                    self.rules['allow'] = []
                self.rules['allow'].append(re.escape(path))
        elif line.lower().startswith('crawl-delay:'):
            self.crawl_delay = int(line.split(':', 1)[1].strip())

    def is_allowed(self, url):
        path = urlparse(url).path
        if 'allow' in self.rules:
            for rule in self.rules['allow']:
                if re.match(rule, path):
                    return True
        if 'disallow' in self.rules:
            for rule in self.rules['disallow']:
                if re.match(rule, path):
                    return False
        return True

    def get_crawl_delay(self):
        return self.crawl_delay

    def get_sitemaps(self):
        return self.sitemaps

class Crawler:
    def __init__(self, base_url, user_agent="*"):
        self.base_url = base_url
        self.visited_urls = set()
        self.to_crawl = set()
        self.robots_parser = RobotsParser(user_agent=user_agent)
        self.robots_parser.fetch_robots(self.base_url)

    def crawl(self, url):
        if not self.robots_parser.is_allowed(url):
            print(f"URL disallowed by robots.txt: {url}")
            return

        delay = self.robots_parser.get_crawl_delay()
        if delay:
            print(f"Respecting crawl delay: {delay} seconds")
            time.sleep(delay)

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"Successfully crawled: {url}")
                self.visited_urls.add(url)
                links = self.extract_links(response.content, url)
                self.to_crawl.update(links)
                self.to_crawl.difference_update(self.visited_urls)
            else:
                print(f"Failed to crawl {url}, status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error crawling {url}: {e}")

    def extract_links(self, html_content, base_url):
        soup = BeautifulSoup(html_content, "html.parser")
        links = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                links.add(full_url)
        return links

    def start_crawling(self, initial_url=None, max_pages=10):
        if initial_url is None:
            initial_url = self.base_url

        self.to_crawl.add(initial_url)
        pages_crawled = 0

        while self.to_crawl and pages_crawled < max_pages:
            url = self.to_crawl.pop()
            if url not in self.visited_urls:
                self.crawl(url)
                pages_crawled += 1
        print(f"Finished crawling {pages_crawled} pages")

    def get_sitemap_urls(self):
        return self.robots_parser.get_sitemaps()

if __name__ == "__main__":
    base_url = "https://website.com"
    crawler = Crawler(base_url)

    sitemap_urls = crawler.get_sitemap_urls()
    if sitemap_urls:
        for sitemap in sitemap_urls:
            print(f"Found sitemap: {sitemap}")

    crawler.start_crawling(max_pages=20)