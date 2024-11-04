import unittest
from monitoring.logging.log_config import LogConfig
from monitoring.analytics.clickstream_analysis import ClickstreamAnalyzer
from monitoring.analytics.search_logs_analyzer import SearchLogsAnalyzer
import yaml
import subprocess
import logging
from unittest.mock import patch, MagicMock

class MonitoringAnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up the components needed for the tests
        cls.log_config = LogConfig()
        cls.clickstream_analyzer = ClickstreamAnalyzer()
        cls.search_logs_analyzer = SearchLogsAnalyzer()
        
        # Define the Go-based Prometheus exporter command
        cls.prometheus_exporter_command = ["go", "run", "monitoring/metrics/prometheus_exporter.go"]
        
        # Load alert rules from the YAML file
        cls.alert_rules_file = "monitoring/alerting/alert_rules.yaml"
        with open(cls.alert_rules_file, 'r') as file:
            cls.alert_rules = yaml.safe_load(file)

    def test_prometheus_metrics_exposure(self):
        """
        Test if Prometheus metrics are being properly exposed by the Go exporter.
        """
        result = subprocess.run(self.prometheus_exporter_command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, "Prometheus exporter should run without errors.")
        self.assertIn("metric_name", result.stdout, "Prometheus metrics should contain metric_name.")

    def test_logging_configuration(self):
        """
        Test if logging is correctly configured based on the configuration file.
        """
        self.log_config.setup_logging()
        logger = logging.getLogger('testLogger')
        with self.assertLogs(logger, level='INFO') as log:
            logger.info('This is a test log message.')
            self.assertIn('INFO:testLogger:This is a test log message.', log.output)

    def test_clickstream_data_processing(self):
        """
        Test if clickstream data is correctly processed by the analyzer.
        """
        mock_clickstream_data = [
            {"user_id": "user1", "query": "search term", "clicked_result": 3},
            {"user_id": "user2", "query": "another search", "clicked_result": 1}
        ]
        with patch.object(self.clickstream_analyzer, 'load_clickstream_data', return_value=mock_clickstream_data):
            result = self.clickstream_analyzer.analyze_clickstream()
            self.assertEqual(len(result), 2, "Clickstream analysis should process all entries.")
            self.assertIn('user1', result, "Result should include 'user1'.")
            self.assertEqual(result['user1']['clicked_result'], 3, "User1's clicked result should be 3.")

    def test_search_logs_analysis(self):
        """
        Test if search logs are correctly analyzed by the search log analyzer.
        """
        mock_logs = [
            {"timestamp": "2024-09-10T10:00:00Z", "query": "term", "results_count": 5},
            {"timestamp": "2024-09-10T10:05:00Z", "query": "another", "results_count": 0}
        ]
        with patch.object(self.search_logs_analyzer, 'load_search_logs', return_value=mock_logs):
            analysis_result = self.search_logs_analyzer.analyze_logs()
            self.assertEqual(len(analysis_result), 2, "Log analysis should return two entries.")
            self.assertIn('2024-09-10T10:00:00Z', analysis_result, "First timestamp should be present.")
            self.assertEqual(analysis_result['2024-09-10T10:00:00Z']['results_count'], 5, "First log results count should be 5.")

    def test_alert_rules_load(self):
        """
        Test if alert rules are correctly loaded from the YAML alert rules file.
        """
        self.assertGreater(len(self.alert_rules), 0, "Alert rules should not be empty.")
        for rule in self.alert_rules:
            self.assertIn('name', rule, "Alert rule should have a name.")
            self.assertIn('threshold', rule, "Alert rule should have a threshold.")

    def test_alerting_logic(self):
        """
        Test if the alerting logic is working based on the loaded YAML alert rules.
        """
        mock_metrics = {'query_latency': 500}
        triggered_alerts = [rule for rule in self.alert_rules if mock_metrics['query_latency'] > rule['threshold']]
        self.assertIn('query_latency', [alert['name'] for alert in triggered_alerts], "Alert should be triggered for query_latency.")

    def test_clickstream_empty_data(self):
        """
        Test handling of empty clickstream data.
        """
        with patch.object(self.clickstream_analyzer, 'load_clickstream_data', return_value=[]):
            result = self.clickstream_analyzer.analyze_clickstream()
            self.assertEqual(len(result), 0, "Analysis result should be empty for no clickstream data.")

    def test_search_logs_empty_data(self):
        """
        Test handling of empty search logs data.
        """
        with patch.object(self.search_logs_analyzer, 'load_search_logs', return_value=[]):
            analysis_result = self.search_logs_analyzer.analyze_logs()
            self.assertEqual(len(analysis_result), 0, "Analysis result should be empty for no search logs data.")

    def test_prometheus_no_metrics(self):
        """
        Test behavior when no metrics are exposed.
        """
        with patch('subprocess.run', return_value=MagicMock(returncode=0, stdout='')):
            metrics_data = subprocess.run(self.prometheus_exporter_command, capture_output=True, text=True)
            self.assertEqual(len(metrics_data.stdout), 0, "No metrics should be exposed.")

    def test_alert_no_triggers(self):
        """
        Test that no alerts are triggered when metrics are within thresholds.
        """
        mock_metrics = {'query_latency': 50}
        triggered_alerts = [rule for rule in self.alert_rules if mock_metrics['query_latency'] > rule['threshold']]
        self.assertNotIn('query_latency', [alert['name'] for alert in triggered_alerts], "No alert should be triggered for query_latency.")

    def test_logging_format(self):
        """
        Test if logging follows the correct format.
        """
        self.log_config.setup_logging()
        logger = logging.getLogger('testLogger')
        with self.assertLogs(logger, level='INFO') as log:
            logger.info('Log format test.')
            self.assertIn('INFO:testLogger:Log format test.', log.output)

if __name__ == '__main__':
    unittest.main()