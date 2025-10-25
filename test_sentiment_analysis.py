import unittest
import argparse
from sentiment_analysis import NewsSentimentScanner

class TestSentimentAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up class-level resources, including the FinBERT model."""
        print("\nLoading FinBERT model for testing... (this may take a moment)")
        finbert_config = argparse.Namespace(
            analyzer='finbert',
            format='text',
            file_path=None
        )
        cls.finbert_scanner = NewsSentimentScanner(finbert_config)

    def setUp(self):
        """Set up a mock config for the VADER scanner for each test."""
        vader_config = argparse.Namespace(
            analyzer='vader',
            format='text',
            file_path=None
        )
        self.vader_scanner = NewsSentimentScanner(vader_config)

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

if __name__ == '__main__':
    unittest.main()