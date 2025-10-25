from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import argparse

from sentiment_analysis import NewsSentimentScanner

app = FastAPI(
    title="News Sentiment API",
    description="API for fetching news and analyzing sentiment.",
    version="1.0.0",
)

class ScanRequest(BaseModel):
    market: str = Field(default="gold", description="The market topic to search for.")
    num_articles: int = Field(default=10, ge=1, description="Number of articles to fetch per query.")
    workers: int = Field(default=10, ge=1, description="Number of concurrent workers.")
    analyzer: str = Field(default="vader", pattern="^(vader|finbert)$", description="Sentiment analyzer to use.")
    max_age: Optional[str] = Field(default='7d', description="Maximum age of articles (e.g., 1h, 5d, 2w, 1m, 1y).")

@app.post("/scan", response_model=dict)
async def scan_sentiment(request: ScanRequest):
    """Analyze news sentiment based on the provided parameters."""
    try:
        # Convert Pydantic model to argparse.Namespace-like object
        config = argparse.Namespace(
            market=request.market,
            num_articles=request.num_articles,
            workers=request.workers,
            format='json', # API always returns JSON
            analyzer=request.analyzer,
            file_path=None, # API does not write to file directly
            max_age=request.max_age,
        )
        
        scanner = NewsSentimentScanner(config)
        results = scanner.run(return_json=True)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
