import unittest
import argparse
import json
import numpy as np
from unittest.mock import patch, MagicMock

from sentiment_analysis import NewsSentimentScanner

class TestSentimentAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up class-level resources, including the FinBERT model."""
        print("\nLoading FinBERT model for testing... (this may take a moment)")
        finbert_config = argparse.Namespace(
            analyzer='finbert',
            format='text',
            file_path=None,
            max_age='7d'
        )
        cls.finbert_scanner = NewsSentimentScanner(finbert_config)

    def setUp(self):
        """Set up a mock config for the VADER scanner for each test."""
        self.vader_config = argparse.Namespace(
            analyzer='vader',
            format='text',
            file_path=None,
            max_age='7d'
        )
        self.vader_scanner = NewsSentimentScanner(self.vader_config)

    def test_vader_positive(self):
        """Test VADER with a clearly positive sentence."""
        polarity, sentiment = self.vader_scanner.analyzer_func("This is a wonderful and amazing development.")
        self.assertEqual(sentiment, 'Positive')
        self.assertGreater(polarity, 0.05)

    def test_vader_negative(self):
        """Test VADER with a clearly negative sentence."""
        polarity, sentiment = self.vader_scanner.analyzer_func("This is a terrible and dreadful development.")
        self.assertEqual(sentiment, 'Negative')
        self.assertLess(polarity, -0.05)

    def test_vader_neutral(self):
        """Test VADER with a neutral sentence."""
        polarity, sentiment = self.vader_scanner.analyzer_func("The report was published yesterday.")
        self.assertEqual(sentiment, 'Neutral')

    def test_finbert_positive(self):
        """Test FinBERT with a positive financial sentence."""
        polarity, sentiment = self.finbert_scanner.analyzer_func("Earnings per share have increased significantly year over year.")
        self.assertEqual(sentiment, 'Positive')
        self.assertGreater(polarity, 0)

    def test_finbert_negative(self):
        """Test FinBERT with a negative financial sentence."""
        polarity, sentiment = self.finbert_scanner.analyzer_func("The company announced a major loss and widespread layoffs.")
        self.assertEqual(sentiment, 'Negative')
        self.assertLess(polarity, 0)

    def test_finbert_neutral(self):
        """Test FinBERT with a neutral financial sentence."""
        polarity, sentiment = self.finbert_scanner.analyzer_func("The stock is traded on the NASDAQ stock exchange.")
        self.assertEqual(sentiment, 'Neutral')

    def test_summary_calculations(self):
        """Test the average and standard deviation calculations in the summary."""
        articles = [
            {'sentiment': 'Positive', 'polarity': 0.8},
            {'sentiment': 'Positive', 'polarity': 0.6},
            {'sentiment': 'Negative', 'polarity': -0.4},
            {'sentiment': 'Negative', 'polarity': -0.2},
            {'sentiment': 'Neutral', 'polarity': 0.0},
        ]
        
        config = argparse.Namespace(format='json', file_path=None, analyzer='vader', max_age='7d')
        scanner = NewsSentimentScanner(config)
        
        with patch('builtins.print') as mock_print:
            scanner._output_results(articles)
            output_json = mock_print.call_args[0][0]
            results = json.loads(output_json)

        summary = results['summary']
        scores = [0.8, 0.6, -0.4, -0.2, 0.0]
        self.assertAlmostEqual(summary['average_sentiment'], np.mean(scores), places=5)
        self.assertAlmostEqual(summary['sentiment_std_dev'], np.std(scores), places=5)
        self.assertEqual(summary['total_analyzed'], 5)

    @patch('sentiment_analysis.feedparser.parse')
    def test_max_age_url_formatting(self, mock_feedparser_parse):
        """Test that the max_age parameter is correctly formatted into the RSS URL."""
        mock_feedparser_parse.return_value = MagicMock(entries=[])

        test_cases = {
            '5d': 'qdr:d5',
            '10h': 'qdr:h10',
            '1m': 'qdr:m1',
        }

        for max_age_input, expected_tbs in test_cases.items():
            with self.subTest(max_age=max_age_input):
                config = argparse.Namespace(num_articles=1, max_age=max_age_input, analyzer='vader', file_path=None)
                scanner = NewsSentimentScanner(config)
                scanner._fetch_news_items("test query")
                call_args, _ = mock_feedparser_parse.call_args
                self.assertIn(f"&tbs={expected_tbs}", call_args[0])

if __name__ == '__main__':
    unittest.main()
