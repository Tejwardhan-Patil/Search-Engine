import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import json
from typing import List, Dict, Optional

class ContentExtractor:
    def __init__(self, user_agent: str = "ContentExtractorBot/1.0"):
        self.headers = {"User-Agent": user_agent}
        self.og_tags = ['og:title', 'og:description', 'og:image', 'og:url']

    def fetch_page(self, url: str) -> Optional[str]:
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to fetch {url} with status code {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_html(self, html: str, url: str) -> Dict:
        soup = BeautifulSoup(html, 'html.parser')
        title = self.extract_title(soup)
        description = self.extract_meta_description(soup)
        content = self.extract_content(soup)
        metadata = self.extract_metadata(soup, url)
        og_data = self.extract_opengraph_data(soup)

        return {
            "url": url,
            "title": title,
            "description": description,
            "content": content,
            "metadata": metadata,
            "og_data": og_data
        }

    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        if soup.title:
            return soup.title.get_text().strip()
        return None

    def extract_meta_description(self, soup: BeautifulSoup) -> Optional[str]:
        description = soup.find("meta", attrs={"name": "description"})
        if description and description.get("content"):
            return description["content"].strip()
        return None

    def extract_content(self, soup: BeautifulSoup) -> str:
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract visible text
        text = soup.get_text(separator=' ')
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return ' '.join(lines)

    def extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        canonical_url = self.extract_canonical_url(soup, url)
        word_count = self.get_word_count(soup)
        headings = self.extract_headings(soup)
        links = self.extract_links(soup, url)

        return {
            "canonical_url": canonical_url,
            "word_count": word_count,
            "headings": headings,
            "links": links
        }

    def extract_canonical_url(self, soup: BeautifulSoup, url: str) -> str:
        canonical_tag = soup.find("link", rel="canonical")
        if canonical_tag and canonical_tag.get("href"):
            return canonical_tag["href"]
        return url

    def get_word_count(self, soup: BeautifulSoup) -> int:
        text = self.extract_content(soup)
        words = re.findall(r'\w+', text)
        return len(words)

    def extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        headings = {}
        for level in range(1, 7):
            heading_tag = f"h{level}"
            headings[heading_tag] = [h.get_text().strip() for h in soup.find_all(heading_tag)]
        return headings

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        links = []
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            full_url = urljoin(base_url, href)
            if self.is_valid_url(full_url):
                links.append(full_url)
        return links

    def is_valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])

    def extract_opengraph_data(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        og_data = {}
        for tag in self.og_tags:
            meta_tag = soup.find("meta", property=tag)
            if meta_tag and meta_tag.get("content"):
                og_data[tag] = meta_tag["content"]
        return og_data

    def clean_url(self, url: str) -> str:
        parsed_url = urlparse(url)
        clean_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
        return clean_url

    def extract_keywords(self, soup: BeautifulSoup) -> Optional[List[str]]:
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords and meta_keywords.get("content"):
            return [kw.strip() for kw in meta_keywords["content"].split(",")]
        return None

    def extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        images = []
        for img_tag in soup.find_all("img", src=True):
            src = img_tag["src"]
            img_url = urljoin(base_url, src)
            if self.is_valid_url(img_url):
                images.append(img_url)
        return images

    def extract_favicon(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        icon_link = soup.find("link", rel="icon")
        if icon_link and icon_link.get("href"):
            return urljoin(base_url, icon_link["href"])
        return None

    def extract_published_date(self, soup: BeautifulSoup) -> Optional[str]:
        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            return time_tag["datetime"]
        return None

    def save_content(self, content: Dict, output_file: str) -> None:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=4)

    def process_url(self, url: str, output_file: str) -> None:
        html = self.fetch_page(url)
        if html:
            parsed_content = self.parse_html(html, url)
            self.save_content(parsed_content, output_file)
        else:
            print(f"Failed to process {url}")

if __name__ == "__main__":
    url_list = ["https://website.com/page1", "https://website.com/page2"]
    extractor = ContentExtractor()

    for url in url_list:
        output_filename = f"output_{extractor.clean_url(url).replace('https://', '').replace('/', '_')}.json"
        extractor.process_url(url, output_filename)