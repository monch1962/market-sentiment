import pytest
import json
from unittest.mock import patch, MagicMock
import argparse
import numpy as np
from fastapi.testclient import TestClient

from api import app
from sentiment_analysis import NewsSentimentScanner

# Fixture for the test client
@pytest.fixture(scope="module")
def client():
    with TestClient(app=app) as client:
        yield client

# Mock for NewsSentimentScanner.run to avoid actual network calls
@pytest.fixture
def mock_scanner_run():
    with patch.object(NewsSentimentScanner, 'run') as mock_run:
        # Configure mock to return a predictable JSON structure
        mock_run.return_value = {
            "summary": {
                "total_analyzed": 1,
                "positive": 1,
                "negative": 0,
                "neutral": 0,
                "average_sentiment": 0.5,
                "sentiment_std_dev": 0.0,
                "max_age_filter": "7d"
            },
            "articles": [
                {
                    "title": "Test Article",
                    "link": "http://test.com",
                    "published": "2025-10-25",
                    "content": "This is a positive test.",
                    "polarity": 0.5,
                    "sentiment": "Positive"
                }
            ]
        }
        yield mock_run

# Mock for NewsSentimentScanner._get_analyzer to avoid model loading
@pytest.fixture
def mock_get_analyzer():
    with patch.object(NewsSentimentScanner, '_get_analyzer') as mock_analyzer:
        mock_analyzer.return_value = lambda text: (0.5, "Positive") # Mock a simple analyzer
        yield mock_analyzer

def test_health_endpoint(client):
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_root_endpoint_webform(client):
    """Test the root endpoint serves the webform."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']
    assert "<form id=\"sentimentForm\">" in response.text

def test_scan_endpoint_success(client, mock_scanner_run, mock_get_analyzer):
    """Test the /scan endpoint with a valid payload for success."""
    payload = {
        "market": "TestMarket",
        "num_articles": 1,
        "analyzer": "vader",
        "max_age": "1d"
    }
    response = client.post("/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "articles" in data
    assert data["summary"]["total_analyzed"] == 1
    mock_scanner_run.assert_called_once_with(return_json=True)

def test_scan_endpoint_validation_error(client):
    """Test the /scan endpoint with an invalid payload for validation error."""
    payload = {
        "market": "TestMarket",
        "num_articles": "invalid", # Invalid type
        "analyzer": "vader"
    }
    response = client.post("/scan", json=payload)
    assert response.status_code == 422 # Unprocessable Entity
    data = response.json()
    assert "detail" in data
    assert "num_articles" in data["detail"][0]["loc"]

def test_scan_endpoint_finbert_analyzer(client, mock_scanner_run, mock_get_analyzer):
    """Test the /scan endpoint with finbert analyzer specified."""
    payload = {
        "market": "TestMarket",
        "num_articles": 1,
        "analyzer": "finbert",
        "max_age": "1d"
    }
    response = client.post("/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["max_age_filter"] == "7d" # Default from NewsSentimentScanner config
    mock_scanner_run.assert_called_once_with(return_json=True)

if __name__ == '__main__':
    pytest.main()
