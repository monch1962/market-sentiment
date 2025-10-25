import feedparser
from newspaper import Article
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from urllib.parse import quote
import argparse
import json
import sys
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

# Defer import of torch until needed

class NewsSentimentScanner:
    def __init__(self, config):
        self.config = config
        self.analyzer_func = self._get_analyzer()

    def _get_analyzer(self):
        if self.config.analyzer == 'finbert':
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            self._log_status("Loading FinBERT model... (this may take a moment)")
            model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
            tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
            return lambda text: self._analyze_sentiment_finbert(text, model, tokenizer)
        else:
            return self._analyze_sentiment_vader

    def _log_status(self, message):
        if self.config.format == 'text' or self.config.file_path:
            print(message, file=sys.stderr)

    def _analyze_sentiment_vader(self, text):
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(text)
        polarity = scores['compound']
        if polarity > 0.05:
            sentiment = 'Positive'
        elif polarity < -0.05:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        return polarity, sentiment

    def _analyze_sentiment_finbert(self, text, model, tokenizer):
        import torch
        if not text.strip():
            return 0.0, 'Neutral'
        
        labels = ['Neutral', 'Positive', 'Negative']
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1).numpy()[0]
        max_index = np.argmax(probabilities)
        sentiment = labels[max_index]
        confidence = probabilities[max_index]
        
        if sentiment == 'Positive':
            polarity = confidence
        elif sentiment == 'Negative':
            polarity = -confidence
        else:
            polarity = 0.0

        return float(polarity), sentiment

    def _fetch_news_items(self, query):
        rss_url = f"https://news.google.com/rss/search?q={quote(query)}"
        if self.config.max_age:
            try:
                match = re.match(r"(\d+)([hdwmy])", self.config.max_age.lower())
                if match:
                    number, letter = match.groups()
                    tbs_param = f"qdr:{letter}{number}"
                    rss_url += f"&tbs={tbs_param}"
                else:
                    self._log_status(f"Warning: Invalid max_age format '{self.config.max_age}'. Ignoring.")
            except Exception as e:
                self._log_status(f"Warning: Could not parse max_age. Ignoring. Error: {e}")

        feed = feedparser.parse(rss_url)
        return feed.entries[:self.config.num_articles]

    def _fetch_article_content(self, url):
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            return f"Content not retrieved due to an error: {e}"

    def run(self, return_json=False):
        market = self.config.market
        
        neutral_queries = [
            f'{market} market news',
            f'{market} price analysis',
            f'{market} trends',
            f'{market} forecast'
        ]
        
        bullish_queries = [
            f'{market} price surge OR rally',
            f'{market} market outperforms',
            f'"strong growth" {market}',
            f'{market} optimism OR bullish',
            f'"record high" {market}'
        ]
        
        bearish_queries = [
            f'{market} price crash OR slump',
            f'{market} market bubble OR downturn',
            f'"fears of" {market} price',
            f'{market} volatility OR concerns',
            f'{market} pessimism OR bearish'
        ]
        
        queries = neutral_queries + bullish_queries + bearish_queries

        self._log_status(f"Fetching news for market: '{self.config.market}'...")

        all_news_items = []
        with ThreadPoolExecutor(max_workers=self.config.workers) as executor:
            future_to_query = {executor.submit(self._fetch_news_items, query): query for query in queries}
            for future in as_completed(future_to_query):
                try:
                    all_news_items.extend(future.result())
                except Exception as e:
                    self._log_status(f"Error fetching news for query '{future_to_query[future]}': {e}")

        self._log_status(f"Found {len(all_news_items)} total articles. Fetching content...")

        articles = []
        with ThreadPoolExecutor(max_workers=self.config.workers) as executor:
            future_to_item = {executor.submit(self._fetch_article_content, item.link): item for item in all_news_items}
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    content = future.result()
                    article_data = {"title": item.title, "link": item.link, "published": item.published, "content": content}
                    
                    text_to_analyze = item.title
                    if "Content not retrieved" not in content and content:
                        text_to_analyze += ' ' + content
                    
                    polarity, sentiment = self.analyzer_func(text_to_analyze)
                    article_data['polarity'] = polarity
                    article_data['sentiment'] = sentiment
                    articles.append(article_data)
                except Exception as e:
                    self._log_status(f"Error processing article '{item.title}': {e}")
        
        return self._output_results(articles, return_json=return_json)

    def _output_results(self, articles, return_json=False):
        summary = {"Positive": 0, "Negative": 0, "Neutral": 0}
        polarity_scores = []
        for article in articles:
            if article.get('sentiment'):
                summary[article['sentiment']] += 1
                polarity_scores.append(article['polarity'])

        analyzed_articles_count = len(polarity_scores)
        average_sentiment = np.mean(polarity_scores) if polarity_scores else 0.0
        sentiment_std_dev = np.std(polarity_scores) if polarity_scores else 0.0

        output_target = self.config.file_path
        
        results = {
            'summary': {
                'total_analyzed': analyzed_articles_count,
                'positive': summary['Positive'],
                'negative': summary['Negative'],
                'neutral': summary['Neutral'],
                'average_sentiment': float(average_sentiment),
                'sentiment_std_dev': float(sentiment_std_dev),
                'max_age_filter': self.config.max_age
            },
            'articles': articles
        }

        if return_json:
            return results

        if self.config.format == 'json':
            if output_target:
                with open(output_target, 'w') as f:
                    json.dump(results, f, indent=4)
                self._log_status(f"Output saved to {output_target}")
            else:
                print(json.dumps(results, indent=4))
        else: # text format
            output_lines = []
            output_lines.append("--- Analysis Results ---")
            for idx, article in enumerate(articles, 1):
                output_lines.append(f"\nArticle {idx}: {article['title']}")
                output_lines.append(f"Link: {article['link']}")
                if 'sentiment' in article:
                    score_label = "Confidence" if self.config.analyzer == 'finbert' else "Polarity"
                    score = article['polarity']
                    output_lines.append(f"Sentiment: {article['sentiment']} ({score_label}: {score:.2f})")
                else:
                    output_lines.append(f"Status: Could not be analyzed.")

            output_lines.append(f"\n--- Market Sentiment Summary (using {self.config.analyzer}) ---")
            if analyzed_articles_count == 0:
                output_lines.append("No articles could be analyzed.")
            else:
                output_lines.append(f"Total articles successfully analyzed: {analyzed_articles_count}")
                output_lines.append(f"Time Filter: {self.config.max_age}")
                for sentiment, count in summary.items():
                    percent = (count / analyzed_articles_count) * 100 if analyzed_articles_count > 0 else 0
                    output_lines.append(f"{sentiment}: {count} ({percent:.2f}%)")
                output_lines.append(f"\nAverage Sentiment (-1 to 1): {average_sentiment:.3f}")
                output_lines.append(f"Sentiment Standard Deviation: {sentiment_std_dev:.3f}")
            
            if output_target:
                with open(output_target, 'w') as f:
                    f.write("\n".join(output_lines))
                self._log_status(f"Output saved to {output_target}")
            else:
                print("\n".join(output_lines))

def main():
    parser = argparse.ArgumentParser(description="Analyze news sentiment for a given market.")
    parser.add_argument("-m", "--market", default="gold", help="The market topic to search for.")
    parser.add_argument("-n", "--num_articles", type=int, default=10, help="Number of articles to fetch per query.")
    parser.add_argument("-w", "--workers", type=int, default=10, help="Number of concurrent workers.")
    parser.add_argument("-f", "--format", choices=['text', 'json'], default='text', help="Output format.")
    parser.add_argument("-a", "--analyzer", choices=['vader', 'finbert'], default='vader', help="Sentiment analyzer to use.")
    parser.add_argument("-p", "--file_path", type=str, default=None, help="Path to save the output file.")
    parser.add_argument("-t", "--max_age", type=str, default='7d', help="Maximum age of articles (e.g., 1h, 5d, 2w, 1m, 1y).")
    args = parser.parse_args()
    
    scanner = NewsSentimentScanner(args)
    scanner.run()

if __name__ == "__main__":
    main()