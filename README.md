# News Sentiment Scanner

A command-line tool to fetch news articles from Google News, analyze their sentiment, and provide a summary.

## Description

This tool allows users to scan for news related to a specific market topic (e.g., "gold", "AAPL stock"). It fetches a configurable number of articles from various news queries, scrapes their content, and performs sentiment analysis on the text.

The final output is a summary of the overall market sentiment (Positive, Negative, Neutral) based on the analyzed articles, along with a detailed breakdown for each article.

## Features

*   **Concurrent Fetching:** Uses multithreading to fetch news articles and their content quickly and efficiently.
*   **Selectable Analyzers:** Choose between two sentiment analysis engines:
    *   `vader`: A fast, general-purpose sentiment analyzer.
    *   `finbert`: A powerful transformer model fine-tuned on financial text for more accurate domain-specific analysis.
*   **Flexible Output:** Display results in a human-readable `text` format or a machine-readable `json` format.
*   **File Output:** Save the analysis results directly to a file for logging or further processing.
*   **Flexible Time-based Filtering:** Limit searches to articles published within a specific timeframe (e.g., last 5 days, 10 hours, or 1 month).
*   **Configurable:** Control the market topic, number of articles, and more via command-line arguments.
*   **REST API:** Expose the tool's capabilities via a FastAPI web service for programmatic access.
*   **Healthcheck Endpoint:** A simple endpoint to verify the API's operational status.
*   **Webform Interface:** A user-friendly web interface to submit parameters and view sentiment analysis results directly in the browser.
*   **Dockerized Deployment:** Easily build and deploy the API within a Docker container.

## Requirements

The dependencies for this project are listed in `requirements.txt`. You can install them using `uv`:

```bash
uv pip install -r requirements.txt
```

## Usage

### Command-Line Interface (CLI)

The script is run from the command line.

#### Basic Usage

To run an analysis on the default market ("gold") with the default settings:

```bash
python sentiment_analysis.py
```

#### Command-Line Arguments

You can customize the script's behavior with the following arguments:

| Argument | Short Form | Description | Default |
|---|---|---|---|
| `--market` | `-m` | The market topic to search for. | `gold` |
| `--num_articles` | `-n` | Number of articles to fetch per query. | `10` |
| `--workers` | `-w` | Number of concurrent workers for fetching. | `10` |
| `--format` | `-f` | The output format. Choices: `text`, `json`. | `text` |
| `--analyzer` | `-a` | The sentiment analyzer to use. Choices: `vader`, `finbert`. | `vader` |
| `--file_path` | `-p` | Path to save the output file. | `None` |
| `--max_age` | `-t` | Maximum age of articles. Format: a number followed by a letter (h, d, w, m, y). | `7d` |

#### Examples

**1. Analyze news for "Apple stock" using the FinBERT analyzer:**

```bash
python sentiment_analysis.py --market "Apple stock" --analyzer finbert
```

**2. Fetch 5 articles per query for "crude oil" and save the results in JSON format to a file named `oil_sentiment.json`:**

```bash
python sentiment_analysis.py -m "crude oil" -n 5 -f json -p oil_sentiment.json
```

**3. Run an analysis on biotech news from the last 3 weeks:**

```bash
python sentiment_analysis.py -m "biotech" -t 3w
```

**4. Run a highly specific analysis on TSLA news from the last 12 hours:**

```bash
python sentiment_analysis.py --market "TSLA" --analyzer finbert --max_age 12h --num_articles 5
```

### REST API

The tool's capabilities are also exposed via a FastAPI web service, allowing for programmatic access.

#### Running the API Server

To start the API server, navigate to the project's root directory in your terminal and run:

```bash
uvicorn api:app --reload
```

Once the server is running (typically on `http://127.0.0.1:8000`), you can access the interactive API documentation (Swagger UI) by opening your web browser to `http://127.0.0.1:8000/docs`.

#### Healthcheck Endpoint

To check if the API is running and responsive, you can access the healthcheck endpoint:

```bash
curl http://127.0.0.1:8000/health
```

This will return a JSON response like `{"status": "ok"}`.

#### Webform Interface

For a user-friendly way to interact with the API, open your web browser to the root URL:

```
http://127.0.0.1:8000/
```

Here you will find a form to input parameters for sentiment analysis and view the JSON results directly in your browser.

#### Making an API Request

Send a `POST` request to the `/scan` endpoint with a JSON payload containing your desired parameters. All output will be in JSON format.

**Example using `curl`:**

```bash
curl -X POST "http://127.0.0.1:8000/scan" \
     -H "Content-Type: application/json" \
     -d '{ \
           "market": "Apple", \
           "num_articles": 5, \
           "analyzer": "finbert", \
           "max_age": "2d" \
         }'
```

### Dockerization

For easy deployment, the FastAPI application can be built and run inside a Docker container.

#### 1. Build the Docker Image

Navigate to your project's root directory in your terminal (where the `Dockerfile` is located) and run the following command:

```bash
docker build -t news-sentiment-api .
```

#### 2. Run the Docker Container

Once the image is built, you can run your FastAPI application in a container using:

```bash
docker run -p 8000:8000 news-sentiment-api
```

After running this command, your FastAPI server will be accessible at `http://localhost:8000`. You can then open `http://localhost:8000/docs` in your web browser to see the interactive API documentation.