import os
import re
import json
from collections import defaultdict
from datetime import datetime
from statistics import mean, median

# Log File Path
LOG_FILE_PATH = '/mnt/data/search_logs.log'

# Patterns for extracting log information
LOG_PATTERN = r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (?P<user_id>\S+) - (?P<query>.+?) - (?P<results_count>\d+) - (?P<response_time>\d+\.\d+)'

# Class for analyzing search logs
class SearchLogsAnalyzer:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.search_data = []
        self.query_frequency = defaultdict(int)
        self.user_activity = defaultdict(list)

    def parse_log_line(self, line):
        """Parses a single log line using regex."""
        match = re.match(LOG_PATTERN, line)
        if match:
            return {
                'timestamp': datetime.strptime(match.group('timestamp'), '%Y-%m-%d %H:%M:%S'),
                'user_id': match.group('user_id'),
                'query': match.group('query').strip(),
                'results_count': int(match.group('results_count')),
                'response_time': float(match.group('response_time'))
            }
        return None

    def load_logs(self):
        """Loads and parses the log file."""
        if not os.path.exists(self.log_file_path):
            raise FileNotFoundError(f"Log file {self.log_file_path} not found.")
        
        with open(self.log_file_path, 'r') as file:
            for line in file:
                parsed_data = self.parse_log_line(line)
                if parsed_data:
                    self.search_data.append(parsed_data)
                    self.query_frequency[parsed_data['query']] += 1
                    self.user_activity[parsed_data['user_id']].append(parsed_data)

    def total_searches(self):
        """Returns the total number of searches."""
        return len(self.search_data)

    def unique_users(self):
        """Returns the number of unique users."""
        return len(self.user_activity)

    def most_frequent_queries(self, top_n=10):
        """Returns the top N most frequent search queries."""
        sorted_queries = sorted(self.query_frequency.items(), key=lambda x: x[1], reverse=True)
        return sorted_queries[:top_n]

    def user_search_trends(self, user_id):
        """Analyzes search trends for a specific user."""
        if user_id not in self.user_activity:
            return None
        return self.user_activity[user_id]

    def search_response_stats(self):
        """Returns statistics on response times and result counts."""
        response_times = [entry['response_time'] for entry in self.search_data]
        results_counts = [entry['results_count'] for entry in self.search_data]

        stats = {
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'avg_response_time': mean(response_times),
            'median_response_time': median(response_times),
            'min_results_count': min(results_counts),
            'max_results_count': max(results_counts),
            'avg_results_count': mean(results_counts),
            'median_results_count': median(results_counts),
        }
        return stats

    def user_activity_stats(self):
        """Returns activity stats of users."""
        user_stats = {user: len(queries) for user, queries in self.user_activity.items()}
        return sorted(user_stats.items(), key=lambda x: x[1], reverse=True)

    def generate_summary_report(self):
        """Generates a summary report of log analysis."""
        total_searches = self.total_searches()
        unique_users = self.unique_users()
        top_queries = self.most_frequent_queries()
        response_stats = self.search_response_stats()
        user_stats = self.user_activity_stats()

        summary = {
            'total_searches': total_searches,
            'unique_users': unique_users,
            'top_queries': top_queries,
            'response_stats': response_stats,
            'user_stats': user_stats[:5],  # Top 5 most active users
        }
        return summary

    def save_report_to_json(self, report, output_file='search_log_report.json'):
        """Saves the analysis report to a JSON file."""
        with open(output_file, 'w') as file:
            json.dump(report, file, indent=4, default=str)
        print(f"Report saved to {output_file}")

    def search_by_keyword(self, keyword):
        """Searches logs for a specific keyword."""
        results = [entry for entry in self.search_data if keyword.lower() in entry['query'].lower()]
        return results

    def error_analysis(self):
        """Analyzes log errors, if any."""
        error_count = sum(1 for entry in self.search_data if entry['results_count'] == 0)
        return {
            'total_errors': error_count,
            'error_percentage': (error_count / len(self.search_data)) * 100 if self.search_data else 0
        }

# Main function to run the analyzer
def main():
    analyzer = SearchLogsAnalyzer(LOG_FILE_PATH)
    try:
        analyzer.load_logs()

        print("Total searches:", analyzer.total_searches())
        print("Unique users:", analyzer.unique_users())

        print("\nTop 10 Most Frequent Queries:")
        for query, freq in analyzer.most_frequent_queries():
            print(f"Query: {query}, Frequency: {freq}")

        print("\nSearch Response Statistics:")
        response_stats = analyzer.search_response_stats()
        for stat, value in response_stats.items():
            print(f"{stat.replace('_', ' ').title()}: {value}")

        print("\nTop 5 Most Active Users:")
        user_stats = analyzer.user_activity_stats()[:5]
        for user, activity_count in user_stats:
            print(f"User: {user}, Search Count: {activity_count}")

        # Generate and save summary report
        summary_report = analyzer.generate_summary_report()
        analyzer.save_report_to_json(summary_report)

        # Perform search by keyword
        keyword_results = analyzer.search_by_keyword("error")
        print(f"\nSearch results containing 'error': {len(keyword_results)} entries found.")

        # Error analysis
        errors = analyzer.error_analysis()
        print(f"\nError Analysis: {errors['total_errors']} errors found, which is {errors['error_percentage']:.2f}% of total searches.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()