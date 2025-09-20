import os
import json
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Dict, List, Callable
import threading

class NewsFileHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.json'):
            # Small delay to ensure file is fully written
            time.sleep(0.1)
            self.callback(event.src_path)

class NewsMonitor:
    def __init__(self, news_directory="live_news_feed"):
        self.news_directory = news_directory
        self.observer = None
        self.news_items = []
        self.callbacks = []

        # Ensure directory exists
        Path(self.news_directory).mkdir(parents=True, exist_ok=True)

    def add_callback(self, callback: Callable):
        """Add callback function to be called when new news arrives"""
        self.callbacks.append(callback)

    def process_news_file(self, file_path: str):
        """Process a new news file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                news_data = json.load(f)

            # Validate required fields
            required_fields = ['company', 'headline', 'content']
            if not all(field in news_data for field in required_fields):
                print(f"Invalid news file format: {file_path}")
                return

            # Add timestamp if not present
            if 'timestamp' not in news_data:
                news_data['timestamp'] = int(time.time())

            # Add severity if not present
            if 'severity' not in news_data:
                news_data['severity'] = self.assess_severity(news_data['content'])

            self.news_items.append(news_data)
            print(f"📰 New news processed: {news_data['headline']}")

            # Call all registered callbacks
            for callback in self.callbacks:
                try:
                    callback(news_data)
                except Exception as e:
                    print(f"Error in callback: {e}")

        except Exception as e:
            print(f"Error processing news file {file_path}: {e}")

    def assess_severity(self, content: str) -> str:
        """Simple severity assessment based on keywords"""
        high_severity_keywords = [
            'lawsuit', 'fine', 'penalty', 'scandal', 'violation', 'illegal',
            'fraud', 'discrimination', 'harassment', 'breach', 'investigation'
        ]

        medium_severity_keywords = [
            'layoffs', 'closure', 'complaint', 'criticism', 'controversy',
            'dispute', 'delay', 'problem', 'issue'
        ]

        content_lower = content.lower()

        if any(keyword in content_lower for keyword in high_severity_keywords):
            return "HIGH"
        elif any(keyword in content_lower for keyword in medium_severity_keywords):
            return "MEDIUM"
        else:
            return "LOW"

    def start_monitoring(self):
        """Start monitoring the news directory for new files"""
        event_handler = NewsFileHandler(self.process_news_file)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.news_directory, recursive=False)
        self.observer.start()
        print(f"📁 Started monitoring {self.news_directory} for news files...")

    def stop_monitoring(self):
        """Stop monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("Stopped monitoring news directory")

    def get_company_news(self, company_id: str, hours_back: int = 24) -> List[Dict]:
        """Get recent news for a specific company"""
        cutoff_time = time.time() - (hours_back * 3600)

        company_news = [
            item for item in self.news_items
            if item.get('company', '').lower() == company_id.lower()
            and item.get('timestamp', 0) > cutoff_time
        ]

        # Sort by timestamp, newest first
        return sorted(company_news, key=lambda x: x.get('timestamp', 0), reverse=True)

    def create_sample_news(self):
        """Create sample news files for demo"""
        sample_news = [
            {
                "company": "TechCorp",
                "headline": "TechCorp Wins Environmental Award for Green Initiatives",
                "content": "TechCorp was recognized today for its outstanding commitment to environmental sustainability, receiving the Green Tech Award for its renewable energy investments and carbon reduction efforts.",
                "source": "Tech Daily",
                "severity": "LOW",
                "timestamp": int(time.time())
            },
            {
                "company": "TechCorp",
                "headline": "TechCorp Announces Major Layoffs Despite Record Profits",
                "content": "TechCorp announced today that it will lay off 15% of its workforce, approximately 5,000 employees, despite reporting record quarterly profits. The company cited 'cost optimization' as the primary reason.",
                "source": "Business News",
                "severity": "MEDIUM",
                "timestamp": int(time.time()) - 3600  # 1 hour ago
            }
        ]

        for i, news in enumerate(sample_news):
            file_path = Path(self.news_directory) / f"sample_news_{i}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(news, f, indent=2)

        print(f"Created {len(sample_news)} sample news files")

def create_breaking_news(company: str, headline: str, content: str, severity: str = "HIGH"):
    """Utility function to create breaking news during demo"""
    news_data = {
        "company": company,
        "headline": headline,
        "content": content,
        "source": "Breaking News",
        "severity": severity,
        "timestamp": int(time.time())
    }

    file_path = Path("live_news_feed") / f"breaking_{int(time.time())}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, indent=2)

    print(f"🚨 Breaking news created: {headline}")

if __name__ == "__main__":
    # Demo usage
    monitor = NewsMonitor()

    # Create sample news
    monitor.create_sample_news()

    # Add a simple callback
    def news_callback(news_data):
        print(f"🔔 Alert: {news_data['company']} - {news_data['severity']} severity")

    monitor.add_callback(news_callback)

    # Start monitoring
    monitor.start_monitoring()

    try:
        print("Monitoring... Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop_monitoring()