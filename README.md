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

## Requirements

The dependencies for this project are listed in `requirements.txt`. You can install them using pip:

```bash
pip install -r requirements.txt
```

## Usage

The script is run from the command line.

### Basic Usage

To run an analysis on the default market ("gold") with the default settings:

```bash
python sentiment_analysis.py
```

### Command-Line Arguments

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

### Examples

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
