import argparse
import requests
import json
import sys

class SearchCLI:
    def __init__(self):
        self.base_url = "http://website.com/api/search"
        self.query = None
        self.page = 1
        self.results_per_page = 10
        self.verbose = False

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Search CLI tool to interact with the search engine.')
        parser.add_argument('query', type=str, help='Search query to be submitted')
        parser.add_argument('-p', '--page', type=int, default=1, help='Page number for paginated results')
        parser.add_argument('-r', '--results-per-page', type=int, default=10, help='Number of results per page')
        parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
        args = parser.parse_args()

        self.query = args.query
        self.page = args.page
        self.results_per_page = args.results_per_page
        self.verbose = args.verbose

    def format_search_url(self):
        params = {
            'q': self.query,
            'page': self.page,
            'limit': self.results_per_page
        }
        return self.base_url + '?' + '&'.join([f'{k}={v}' for k, v in params.items()])

    def make_request(self):
        search_url = self.format_search_url()
        try:
            if self.verbose:
                print(f"Sending request to: {search_url}")
            response = requests.get(search_url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: Received status code {response.status_code}")
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            sys.exit(1)

    def display_results(self, data):
        if 'results' not in data or not data['results']:
            print("No results found.")
            return
        
        print(f"\nDisplaying results for query: '{self.query}' (Page {self.page})\n")
        for i, result in enumerate(data['results'], start=1):
            print(f"Result {i}:")
            print(f"  Title: {result.get('title', 'No title available')}")
            print(f"  URL: {result.get('url', 'No URL available')}")
            print(f"  Snippet: {result.get('snippet', 'No snippet available')}")
            print(f"  Score: {result.get('score', 'No score available')}\n")

    def run(self):
        self.parse_arguments()
        response_data = self.make_request()
        self.display_results(response_data)


class SearchResultsFormatter:
    def __init__(self, json_data):
        self.data = json_data

    def pretty_format(self):
        formatted_results = []
        for result in self.data.get('results', []):
            title = result.get('title', 'No title')
            url = result.get('url', 'No URL')
            snippet = result.get('snippet', 'No snippet')
            score = result.get('score', 'No score')
            formatted_results.append(f"Title: {title}\nURL: {url}\nSnippet: {snippet}\nScore: {score}\n")
        return "\n".join(formatted_results)

    def save_to_file(self, file_path):
        formatted_results = self.pretty_format()
        with open(file_path, 'w') as f:
            f.write(formatted_results)
        print(f"Results saved to {file_path}")

class InteractiveSearchCLI(SearchCLI):
    def __init__(self):
        super().__init__()
        self.previous_queries = []

    def run(self):
        print("Welcome to the Interactive Search CLI!")
        while True:
            user_input = input("\nEnter a search query (or 'exit' to quit): ").strip()
            if user_input.lower() == 'exit':
                print("Exiting the Interactive Search CLI.")
                break
            elif user_input.lower() == 'history':
                self.display_query_history()
            else:
                self.query = user_input
                self.previous_queries.append(user_input)
                response_data = self.make_request()
                self.display_results(response_data)

    def display_query_history(self):
        if not self.previous_queries:
            print("No search history available.")
        else:
            print("\nSearch Query History:")
            for i, query in enumerate(self.previous_queries, start=1):
                print(f"{i}. {query}")

    def clear_history(self):
        self.previous_queries.clear()
        print("Search history cleared.")


if __name__ == "__main__":
    cli_type = input("Select CLI mode (interactive or standard): ").strip().lower()
    
    if cli_type == 'interactive':
        cli = InteractiveSearchCLI()
    else:
        cli = SearchCLI()
    
    cli.run()