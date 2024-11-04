import time
import requests
import threading
import random
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging to capture load test results
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the search engine's base URL
SEARCH_ENGINE_URL = "http://website.com/search"

# Number of concurrent users for the load test
CONCURRENT_USERS = 200

# Number of total requests per user
REQUESTS_PER_USER = 100

# Query terms for the load test
QUERY_TERMS = [
    "artificial intelligence", "machine learning", "data science", "natural language processing",
    "deep learning", "search engine", "python programming", "cloud computing",
    "big data", "cybersecurity", "blockchain", "robotics", "quantum computing",
    "5G networks", "autonomous vehicles", "virtual reality", "augmented reality", "internet of things"
]

# Random user agent strings to simulate different clients
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.1.2 Safari/602.3.12",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"
]

# Function to simulate a search request
def simulate_search(query, user_agent):
    headers = {
        'User-Agent': user_agent
    }
    params = {
        'query': query,
        'page': random.randint(1, 10)  # Simulating pagination
    }
    try:
        response = requests.get(SEARCH_ENGINE_URL, headers=headers, params=params)
        if response.status_code == 200:
            logging.info(f"Search successful for query: '{query}' with User-Agent: '{user_agent}'")
        else:
            logging.warning(f"Failed search for query: '{query}' with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for query: '{query}' due to {e}")

# Function for a user simulation during the load test
def simulate_user():
    user_agent = random.choice(USER_AGENTS)
    for _ in range(REQUESTS_PER_USER):
        query = random.choice(QUERY_TERMS)
        simulate_search(query, user_agent)
        time.sleep(random.uniform(0.1, 1.0))  # Simulate random delay between searches

# Run the load test with multiple users
def run_load_test():
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        futures = [executor.submit(simulate_user) for _ in range(CONCURRENT_USERS)]
        for future in futures:
            future.result()  # Wait for all users to complete their searches
    end_time = time.time()

    logging.info(f"Load test completed in {end_time - start_time:.2f} seconds")

# Main function to start the load test
if __name__ == "__main__":
    logging.info(f"Starting load test with {CONCURRENT_USERS} users, each making {REQUESTS_PER_USER} requests")
    run_load_test()