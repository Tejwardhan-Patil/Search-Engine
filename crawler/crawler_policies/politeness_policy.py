import time
from urllib.parse import urlparse
import logging

class PolitenessPolicy:
    def __init__(self, user_agent: str, delay: float = 1.0):
        """
        Initializes the politeness policy.
        
        Args:
            user_agent: The user agent to be used for web requests.
            delay: Minimum delay (in seconds) between requests to the same host.
        """
        self.user_agent = user_agent
        self.delay = delay
        self.last_access_times = {}
        self.robots_cache = {}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('PolitenessPolicy')

    def can_fetch(self, url: str) -> bool:
        """
        Determines if the URL can be fetched based on the robots.txt rules.
        
        Args:
            url: The URL to check.

        Returns:
            True if the URL can be fetched, False otherwise.
        """
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        
        if host in self.robots_cache:
            return self.robots_cache[host].can_fetch(self.user_agent, url)
        
        robots_url = f'{parsed_url.scheme}://{host}/robots.txt'
        self.logger.info(f'Fetching robots.txt from {robots_url}')
        
        try:
            robots_parser = RobotsParser(robots_url, self.user_agent)
            self.robots_cache[host] = robots_parser
            return robots_parser.can_fetch(self.user_agent, url)
        except Exception as e:
            self.logger.error(f'Error fetching robots.txt from {robots_url}: {str(e)}')
            return True

    def respect_delay(self, url: str):
        """
        Respects the delay policy by waiting if necessary before making a request.
        
        Args:
            url: The URL that will be requested.
        """
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        current_time = time.time()

        if host in self.last_access_times:
            elapsed_time = current_time - self.last_access_times[host]
            if elapsed_time < self.delay:
                sleep_time = self.delay - elapsed_time
                self.logger.info(f'Sleeping for {sleep_time:.2f} seconds before accessing {host}')
                time.sleep(sleep_time)
        
        self.last_access_times[host] = current_time

class RobotsParser:
    def __init__(self, robots_url: str, user_agent: str):
        """
        Initializes the robots.txt parser.
        
        Args:
            robots_url: URL of the robots.txt file.
            user_agent: The user agent for which the parsing is done.
        """
        self.user_agent = user_agent
        self.disallowed_paths = []
        self.crawl_delay = None
        self.fetch_robots_txt(robots_url)
        
    def fetch_robots_txt(self, robots_url: str):
        """
        Fetches and parses the robots.txt file.
        
        Args:
            robots_url: The URL from which to fetch the robots.txt file.
        """
        try:
            response = self.make_request(robots_url)
            if response.status_code == 200:
                self.parse_robots_txt(response.text)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch robots.txt: {str(e)}")

    def make_request(self, url: str):
        """
        Makes an HTTP request to the given URL.
        
        Args:
            url: The URL to request.
        
        Returns:
            The HTTP response.
        """
        import requests
        headers = {'User-Agent': self.user_agent}
        return requests.get(url, headers=headers)

    def parse_robots_txt(self, robots_txt_content: str):
        """
        Parses the content of the robots.txt file.
        
        Args:
            robots_txt_content: The content of the robots.txt file.
        """
        lines = robots_txt_content.splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.lower().startswith('user-agent:'):
                current_agent = line.split(':', 1)[1].strip()
                applicable = current_agent == '*' or current_agent == self.user_agent
            elif applicable and line.lower().startswith('disallow:'):
                path = line.split(':', 1)[1].strip()
                if path:
                    self.disallowed_paths.append(path)
            elif applicable and line.lower().startswith('crawl-delay:'):
                self.crawl_delay = float(line.split(':', 1)[1].strip())

    def can_fetch(self, user_agent: str, url: str) -> bool:
        """
        Checks whether the user agent is allowed to fetch the given URL.
        
        Args:
            user_agent: The user agent making the request.
            url: The URL to be fetched.
        
        Returns:
            True if the URL is allowed to be fetched, False otherwise.
        """
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        for disallowed_path in self.disallowed_paths:
            if path.startswith(disallowed_path):
                return False
        return True
    
    def get_crawl_delay(self) -> float:
        """
        Returns the crawl delay specified in the robots.txt file.
        
        Returns:
            The crawl delay if specified, or None if not.
        """
        return self.crawl_delay

class PolitenessManager:
    def __init__(self, politeness_policy: PolitenessPolicy):
        """
        Manages politeness across multiple threads or processes.
        
        Args:
            politeness_policy: The PolitenessPolicy object to use for determining delays and robots.txt compliance.
        """
        self.politeness_policy = politeness_policy
        self.logger = logging.getLogger('PolitenessManager')
    
    def fetch_page(self, url: str):
        """
        Fetches a page while respecting politeness policies.
        
        Args:
            url: The URL of the page to fetch.
        
        Returns:
            The content of the fetched page.
        """
        if not self.politeness_policy.can_fetch(url):
            self.logger.info(f"Not allowed to fetch {url} due to robots.txt rules")
            return None
        
        self.politeness_policy.respect_delay(url)
        
        try:
            response = self.make_request(url)
            if response.status_code == 200:
                self.logger.info(f"Successfully fetched {url}")
                return response.content
            else:
                self.logger.error(f"Failed to fetch {url} - Status code: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def make_request(self, url: str):
        """
        Makes an HTTP request to the given URL.
        
        Args:
            url: The URL to request.
        
        Returns:
            The HTTP response.
        """
        import requests
        headers = {'User-Agent': self.politeness_policy.user_agent}
        return requests.get(url, headers=headers)

# Usage
if __name__ == "__main__":
    politeness_policy = PolitenessPolicy(user_agent="SearchEngineBot", delay=2.0)
    manager = PolitenessManager(politeness_policy)
    
    urls = [
        "https://website.com/page1",
        "https://website.com/page2",
        "https://website.com/page3"
    ]
    
    for url in urls:
        page_content = manager.fetch_page(url)
        if page_content:
            print(f"Fetched content from {url}")