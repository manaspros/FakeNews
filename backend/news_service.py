import os
import requests
import feedparser
import asyncio
import aiohttp
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import json
import time
from newsapi import NewsApiClient
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    title: str
    content: str
    url: str
    source: str
    published_at: datetime
    company: str
    sentiment_score: float = 0.0
    relevance_score: float = 0.0
    severity: str = "LOW"  # LOW, MEDIUM, HIGH
    keywords: List[str] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

class NewsService:
    def __init__(self):
        self.setup_apis()
        self.setup_rss_feeds()
        self.keyword_mappings = self._load_keyword_mappings()

    def setup_apis(self):
        """Initialize news API clients"""
        # NewsAPI (Free tier: 100 requests/day)
        self.newsapi_key = os.getenv('NEWS_API_KEY')
        if self.newsapi_key:
            try:
                self.newsapi_client = NewsApiClient(api_key=self.newsapi_key)
                logger.info("NewsAPI initialized")
            except Exception as e:
                logger.error(f"NewsAPI initialization failed: {e}")
                self.newsapi_client = None
        else:
            self.newsapi_client = None

        # NewsData.io (Free tier: 200 requests/day)
        self.newsdata_key = os.getenv('NEWSDATA_API_KEY')

    def setup_rss_feeds(self):
        """Setup RSS feeds for free news sources"""
        self.rss_feeds = {
            'reuters_business': 'https://feeds.reuters.com/reuters/businessNews',
            'reuters_tech': 'https://feeds.reuters.com/reuters/technologyNews',
            'bbc_business': 'http://feeds.bbci.co.uk/news/business/rss.xml',
            'cnn_business': 'http://rss.cnn.com/rss/money_latest.rss',
            'guardian_business': 'https://www.theguardian.com/business/rss',
            'techcrunch': 'https://techcrunch.com/feed/',
            'ars_technica': 'http://feeds.arstechnica.com/arstechnica/index',
            'google_news_business': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZ4ZERBU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en'
        }

    def _load_keyword_mappings(self) -> Dict:
        """Load company and severity keywords"""
        return {
            'companies': {
                'apple': ['apple inc', 'apple corp', 'cupertino'],
                'google': ['google', 'alphabet', 'youtube', 'android'],
                'amazon': ['amazon', 'aws', 'alexa', 'bezos'],
                'microsoft': ['microsoft', 'azure', 'windows', 'xbox'],
                'meta': ['meta', 'facebook', 'instagram', 'whatsapp'],
                'tesla': ['tesla', 'spacex', 'elon musk'],
                'netflix': ['netflix', 'streaming'],
                'uber': ['uber', 'rideshare'],
                'airbnb': ['airbnb'],
                'twitter': ['twitter', 'x corp'],
            },
            'severity': {
                'high': [
                    'lawsuit', 'sued', 'fine', 'penalty', 'violation', 'illegal',
                    'fraud', 'scandal', 'investigation', 'charges', 'criminal',
                    'breach', 'hack', 'data leak', 'privacy violation',
                    'discrimination', 'harassment', 'toxic', 'abuse'
                ],
                'medium': [
                    'layoffs', 'fired', 'closure', 'complaint', 'criticism',
                    'controversy', 'dispute', 'delay', 'problem', 'issue',
                    'protest', 'boycott', 'strike', 'union', 'regulation'
                ],
                'low': [
                    'announcement', 'launch', 'expansion', 'growth',
                    'partnership', 'acquisition', 'investment', 'funding'
                ]
            }
        }

    async def fetch_company_news(self, company: str, days_back: int = 7) -> List[NewsArticle]:
        """Fetch news for a specific company from all sources"""
        articles = []

        # Parallel fetching from different sources
        tasks = [
            self._fetch_from_newsapi(company, days_back),
            self._fetch_from_newsdata(company, days_back),
            self._fetch_from_rss_feeds(company, days_back),
            self._fetch_from_google_rss(company, days_back)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                articles.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"News fetching error: {result}")

        # Remove duplicates and sort by relevance
        unique_articles = self._deduplicate_articles(articles)
        return sorted(unique_articles, key=lambda x: x.relevance_score, reverse=True)

    async def _fetch_from_newsapi(self, company: str, days_back: int) -> List[NewsArticle]:
        """Fetch from NewsAPI"""
        if not self.newsapi_client:
            return []

        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)

            # Search for company news
            response = self.newsapi_client.get_everything(
                q=f'"{company}"',
                language='en',
                sort_by='relevancy',
                from_param=from_date.strftime('%Y-%m-%d'),
                to=to_date.strftime('%Y-%m-%d'),
                page_size=20
            )

            articles = []
            for article in response.get('articles', []):
                news_article = self._parse_newsapi_article(article, company)
                if news_article:
                    articles.append(news_article)

            return articles

        except Exception as e:
            logger.error(f"NewsAPI fetch error: {e}")
            return []

    async def _fetch_from_newsdata(self, company: str, days_back: int) -> List[NewsArticle]:
        """Fetch from NewsData.io"""
        if not self.newsdata_key:
            return []

        try:
            url = "https://newsdata.io/api/1/news"
            params = {
                'apikey': self.newsdata_key,
                'q': f'"{company}"',
                'language': 'en',
                'category': 'business,technology',
                'size': 10
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        for article in data.get('results', []):
                            news_article = self._parse_newsdata_article(article, company)
                            if news_article:
                                articles.append(news_article)
                        return articles

        except Exception as e:
            logger.error(f"NewsData fetch error: {e}")

        return []

    async def _fetch_from_rss_feeds(self, company: str, days_back: int) -> List[NewsArticle]:
        """Fetch from RSS feeds"""
        articles = []

        async def fetch_rss(feed_name, feed_url):
            try:
                # Use asyncio to make RSS parsing non-blocking
                loop = asyncio.get_event_loop()
                feed = await loop.run_in_executor(None, feedparser.parse, feed_url)

                feed_articles = []
                for entry in feed.entries[:20]:  # Limit per feed
                    if self._is_company_relevant(entry, company):
                        article = self._parse_rss_entry(entry, company, feed_name)
                        if article:
                            feed_articles.append(article)

                return feed_articles

            except Exception as e:
                logger.error(f"RSS fetch error for {feed_name}: {e}")
                return []

        # Fetch from all RSS feeds in parallel
        tasks = [fetch_rss(name, url) for name, url in self.rss_feeds.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                articles.extend(result)

        return articles

    async def _fetch_from_google_rss(self, company: str, days_back: int) -> List[NewsArticle]:
        """Fetch from Google News RSS"""
        try:
            # Google News search URL
            query = f'"{company}" OR "{company} inc" OR "{company} corp"'
            url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"

            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, url)

            articles = []
            for entry in feed.entries[:15]:
                article = self._parse_rss_entry(entry, company, 'google_news')
                if article:
                    articles.append(article)

            return articles

        except Exception as e:
            logger.error(f"Google RSS fetch error: {e}")
            return []

    def _parse_newsapi_article(self, article: Dict, company: str) -> Optional[NewsArticle]:
        """Parse NewsAPI article format"""
        try:
            published_at = datetime.fromisoformat(
                article['publishedAt'].replace('Z', '+00:00')
            )

            content = article.get('content') or article.get('description', '')
            title = article.get('title', '')

            return NewsArticle(
                title=title,
                content=content,
                url=article.get('url', ''),
                source=article.get('source', {}).get('name', 'Unknown'),
                published_at=published_at,
                company=company,
                sentiment_score=self._calculate_sentiment(title + ' ' + content),
                relevance_score=self._calculate_relevance(title + ' ' + content, company),
                severity=self._assess_severity(title + ' ' + content),
                keywords=self._extract_keywords(title + ' ' + content)
            )

        except Exception as e:
            logger.error(f"Error parsing NewsAPI article: {e}")
            return None

    def _parse_newsdata_article(self, article: Dict, company: str) -> Optional[NewsArticle]:
        """Parse NewsData.io article format"""
        try:
            published_at = datetime.fromisoformat(article['pubDate'])

            content = article.get('content') or article.get('description', '')
            title = article.get('title', '')

            return NewsArticle(
                title=title,
                content=content,
                url=article.get('link', ''),
                source=article.get('source_id', 'Unknown'),
                published_at=published_at,
                company=company,
                sentiment_score=self._calculate_sentiment(title + ' ' + content),
                relevance_score=self._calculate_relevance(title + ' ' + content, company),
                severity=self._assess_severity(title + ' ' + content),
                keywords=self._extract_keywords(title + ' ' + content)
            )

        except Exception as e:
            logger.error(f"Error parsing NewsData article: {e}")
            return None

    def _parse_rss_entry(self, entry, company: str, source: str) -> Optional[NewsArticle]:
        """Parse RSS feed entry"""
        try:
            # Handle different date formats
            published_at = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'published'):
                try:
                    published_at = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z')
                except:
                    pass

            content = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
            title = getattr(entry, 'title', '')

            return NewsArticle(
                title=title,
                content=content,
                url=getattr(entry, 'link', ''),
                source=source,
                published_at=published_at,
                company=company,
                sentiment_score=self._calculate_sentiment(title + ' ' + content),
                relevance_score=self._calculate_relevance(title + ' ' + content, company),
                severity=self._assess_severity(title + ' ' + content),
                keywords=self._extract_keywords(title + ' ' + content)
            )

        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return None

    def _is_company_relevant(self, entry, company: str) -> bool:
        """Check if RSS entry is relevant to the company"""
        text = (getattr(entry, 'title', '') + ' ' + getattr(entry, 'summary', '')).lower()
        company_keywords = self.keyword_mappings['companies'].get(company.lower(), [company.lower()])

        return any(keyword in text for keyword in company_keywords)

    def _calculate_sentiment(self, text: str) -> float:
        """Simple sentiment analysis"""
        positive_words = ['success', 'growth', 'profit', 'win', 'achievement', 'positive', 'good', 'excellent']
        negative_words = ['failure', 'loss', 'scandal', 'problem', 'bad', 'negative', 'crisis', 'controversy']

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        total_words = len(text.split())
        if total_words == 0:
            return 0.0

        sentiment = (positive_count - negative_count) / max(total_words / 10, 1)
        return max(-1.0, min(1.0, sentiment))

    def _calculate_relevance(self, text: str, company: str) -> float:
        """Calculate article relevance to company"""
        text_lower = text.lower()
        company_keywords = self.keyword_mappings['companies'].get(company.lower(), [company.lower()])

        # Count company mentions
        mention_count = sum(text_lower.count(keyword) for keyword in company_keywords)

        # Boost score for business-relevant terms
        business_terms = ['financial', 'earnings', 'revenue', 'stock', 'shares', 'market', 'business', 'corporate']
        business_count = sum(1 for term in business_terms if term in text_lower)

        relevance_score = (mention_count * 0.5) + (business_count * 0.1)
        return min(1.0, relevance_score)

    def _assess_severity(self, text: str) -> str:
        """Assess news severity"""
        text_lower = text.lower()

        high_count = sum(1 for keyword in self.keyword_mappings['severity']['high'] if keyword in text_lower)
        medium_count = sum(1 for keyword in self.keyword_mappings['severity']['medium'] if keyword in text_lower)

        if high_count >= 2:
            return "HIGH"
        elif high_count >= 1:
            return "HIGH"
        elif medium_count >= 2:
            return "MEDIUM"
        elif medium_count >= 1:
            return "MEDIUM"
        else:
            return "LOW"

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        all_keywords = []
        for severity_level in self.keyword_mappings['severity'].values():
            all_keywords.extend(severity_level)

        text_lower = text.lower()
        found_keywords = [keyword for keyword in all_keywords if keyword in text_lower]

        return list(set(found_keywords))  # Remove duplicates

    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on title similarity"""
        if not articles:
            return []

        unique_articles = []
        seen_titles = set()

        for article in articles:
            # Simple deduplication based on first 50 characters of title
            title_key = article.title[:50].lower().strip()

            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)

        return unique_articles

    def get_trending_companies(self, limit: int = 10) -> List[Dict]:
        """Get trending companies in news"""
        # This would require a more sophisticated implementation
        # For now, return a static list
        return [
            {"company": "Apple", "mention_count": 45, "sentiment": 0.2},
            {"company": "Google", "mention_count": 38, "sentiment": -0.1},
            {"company": "Amazon", "mention_count": 32, "sentiment": 0.1},
            {"company": "Tesla", "mention_count": 28, "sentiment": -0.3},
            {"company": "Microsoft", "mention_count": 25, "sentiment": 0.4},
        ]

# Utility function for testing
async def test_news_service():
    """Test the news service"""
    service = NewsService()

    print("Testing news service...")
    articles = await service.fetch_company_news("Apple", days_back=3)

    print(f"Found {len(articles)} articles for Apple")
    for article in articles[:5]:
        print(f"- {article.title} ({article.severity}) - {article.source}")

if __name__ == "__main__":
    asyncio.run(test_news_service())