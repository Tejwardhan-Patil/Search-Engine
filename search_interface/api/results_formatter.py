import json
from typing import List, Dict

class ResultsFormatter:
    def __init__(self):
        pass

    def format_result(self, result: Dict) -> Dict:
        """
        Formats an individual result entry, ensuring it follows the necessary structure
        for the API response.
        """
        return {
            "title": result.get("title", "Untitled"),
            "url": result.get("url", ""),
            "snippet": result.get("snippet", ""),
            "relevance_score": result.get("relevance_score", 0.0),
            "metadata": result.get("metadata", {}),
            "rank": result.get("rank", None)
        }

    def format_results(self, results: List[Dict]) -> Dict:
        """
        Formats the entire set of results and ensures it conforms to the expected API response.
        """
        formatted_results = [self.format_result(result) for result in results]
        return {
            "total_results": len(results),
            "results": formatted_results
        }

    def format_error(self, error_message: str, status_code: int = 500) -> Dict:
        """
        Formats error responses to ensure consistent error structure for API clients.
        """
        return {
            "error": {
                "message": error_message,
                "code": status_code
            }
        }

def format_search_response(results: List[Dict], error: str = None) -> str:
    """
    High-level function to format the API response. If an error occurs,
    it returns a formatted error response; otherwise, it returns formatted results.
    """
    formatter = ResultsFormatter()

    if error:
        formatted_response = formatter.format_error(error_message=error)
    else:
        formatted_response = formatter.format_results(results=results)

    return json.dumps(formatted_response, indent=4)

# Usage
if __name__ == "__main__":
    # Simulating search results
    sample_results = [
        {
            "title": "Introduction to Search Engines",
            "url": "http://website.com/search_engines",
            "snippet": "This is an introduction to search engine architecture...",
            "relevance_score": 0.92,
            "metadata": {
                "author": "Person1",
                "date": "2024-09-15"
            },
            "rank": 1
        },
        {
            "title": "Search Engine Optimization",
            "url": "http://website.com/seo",
            "snippet": "Learn the key techniques in search engine optimization...",
            "relevance_score": 0.89,
            "metadata": {
                "author": "Person2",
                "date": "2024-09-12"
            },
            "rank": 2
        }
    ]

    # Formatting the results
    formatted_json = format_search_response(results=sample_results)
    print(formatted_json)