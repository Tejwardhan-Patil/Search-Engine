# Web Crawler Documentation

## Overview

The web crawler is responsible for traversing the web, fetching web pages, and extracting relevant content for indexing.

## Components

1. **Crawler Manager (`crawler_manager.py`)**
   - Manages the entire crawling process, coordinating the fetching and extraction of content.

2. **URL Queue (`url_queue.go`)**
   - Manages the queue of URLs to be crawled.
   - Utilizes Go's concurrency features to efficiently handle large numbers of URLs.

3. **Page Fetcher (`page_fetcher.py`)**
   - Fetches web pages based on URLs from the queue.
   - Includes error handling for HTTP request failures.

4. **Content Extractor (`content_extractor.py`)**
   - Extracts text, metadata, and other relevant information from fetched web pages.

5. **Politeness Policy (`politeness_policy.py`)**
   - Ensures that crawling respects delays between requests to avoid overwhelming web servers.

6. **Robots.txt Parser (`robots_parser.py`)**
   - Parses `robots.txt` files to determine which parts of a website can be crawled.

## Crawling Process

1. **Initialization**: Seed URLs are added to the queue.
2. **Fetching**: The fetcher retrieves the web pages from the seed URLs.
3. **Extraction**: Content is extracted from the pages.
4. **Politeness**: The crawler waits between requests according to the politeness policy.
5. **Storage**: Extracted content is passed to the indexing system for storage.
