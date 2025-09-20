from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hypocrisy_detector.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    industry = Column(String)
    website = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class CompanyDocument(Base):
    __tablename__ = "company_documents"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    document_type = Column(String)  # ESG, Code of Conduct, etc.
    title = Column(String)
    content = Column(Text)
    source_url = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    title = Column(String)
    content = Column(Text)
    url = Column(String)
    source = Column(String)
    published_at = Column(DateTime)
    sentiment_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    severity = Column(String, default="LOW")
    keywords = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class ContradictionAnalysis(Base):
    __tablename__ = "contradiction_analyses"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    query = Column(String)
    contradiction_level = Column(String)  # NONE, LOW, MEDIUM, HIGH
    confidence_score = Column(Float)
    analysis = Column(Text)
    promises_excerpt = Column(Text)
    actions_excerpt = Column(Text)
    key_contradictions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    alert_type = Column(String)  # CONTRADICTION, NEWS, SEVERITY
    level = Column(String)  # LOW, MEDIUM, HIGH
    title = Column(String)
    message = Column(Text)
    data = Column(JSON)
    is_read = Column(Integer, default=0)  # SQLite doesn't have boolean
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database utility functions
class DatabaseManager:
    def __init__(self):
        self.engine = engine

    def get_session(self) -> Session:
        return SessionLocal()

    def add_company(self, name: str, description: str = "", industry: str = "", website: str = "") -> Company:
        with self.get_session() as db:
            existing = db.query(Company).filter(Company.name == name).first()
            if existing:
                return existing

            company = Company(
                name=name,
                description=description,
                industry=industry,
                website=website
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            return company

    def add_company_document(self, company_name: str, doc_type: str, title: str,
                           content: str, source_url: str = "", file_path: str = "") -> CompanyDocument:
        with self.get_session() as db:
            document = CompanyDocument(
                company_name=company_name,
                document_type=doc_type,
                title=title,
                content=content,
                source_url=source_url,
                file_path=file_path
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            return document

    def add_news_article(self, article_data: dict) -> NewsArticle:
        with self.get_session() as db:
            # Check for duplicates (only if URL is not empty)
            url = article_data.get('url', '')
            if url:  # Only check for duplicates if URL exists
                existing = db.query(NewsArticle).filter(
                    NewsArticle.url == url,
                    NewsArticle.company_name == article_data.get('company_name')
                ).first()

                if existing:
                    return existing

            article = NewsArticle(**article_data)
            db.add(article)
            db.commit()
            db.refresh(article)
            return article

    def add_contradiction_analysis(self, analysis_data: dict) -> ContradictionAnalysis:
        with self.get_session() as db:
            analysis = ContradictionAnalysis(**analysis_data)
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            return analysis

    def add_alert(self, company_name: str, alert_type: str, level: str,
                 title: str, message: str, data: dict = None) -> Alert:
        with self.get_session() as db:
            alert = Alert(
                company_name=company_name,
                alert_type=alert_type,
                level=level,
                title=title,
                message=message,
                data=data or {}
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            return alert

    def get_companies(self) -> list:
        with self.get_session() as db:
            return db.query(Company).all()

    def get_company_documents(self, company_name: str) -> list:
        with self.get_session() as db:
            return db.query(CompanyDocument).filter(
                CompanyDocument.company_name == company_name
            ).all()

    def get_recent_news(self, company_name: str = None, limit: int = 50) -> list:
        with self.get_session() as db:
            query = db.query(NewsArticle)
            if company_name:
                query = query.filter(NewsArticle.company_name == company_name)
            return query.order_by(NewsArticle.published_at.desc()).limit(limit).all()

    def get_recent_analyses(self, company_name: str = None, limit: int = 20) -> list:
        with self.get_session() as db:
            query = db.query(ContradictionAnalysis)
            if company_name:
                query = query.filter(ContradictionAnalysis.company_name == company_name)
            return query.order_by(ContradictionAnalysis.created_at.desc()).limit(limit).all()

    def get_unread_alerts(self, company_name: str = None) -> list:
        with self.get_session() as db:
            query = db.query(Alert).filter(Alert.is_read == 0)
            if company_name:
                query = query.filter(Alert.company_name == company_name)
            return query.order_by(Alert.created_at.desc()).all()

    def mark_alert_read(self, alert_id: int):
        with self.get_session() as db:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            if alert:
                alert.is_read = 1
                db.commit()

    def get_company_stats(self, company_name: str) -> dict:
        with self.get_session() as db:
            # Count documents
            doc_count = db.query(CompanyDocument).filter(
                CompanyDocument.company_name == company_name
            ).count()

            # Count news articles
            news_count = db.query(NewsArticle).filter(
                NewsArticle.company_name == company_name
            ).count()

            # Count analyses
            analysis_count = db.query(ContradictionAnalysis).filter(
                ContradictionAnalysis.company_name == company_name
            ).count()

            # Get latest contradiction level
            latest_analysis = db.query(ContradictionAnalysis).filter(
                ContradictionAnalysis.company_name == company_name
            ).order_by(ContradictionAnalysis.created_at.desc()).first()

            latest_level = latest_analysis.contradiction_level if latest_analysis else "UNKNOWN"

            return {
                "company_name": company_name,
                "document_count": doc_count,
                "news_count": news_count,
                "analysis_count": analysis_count,
                "latest_contradiction_level": latest_level
            }

    def cleanup_old_data(self, days_old: int = 30):
        """Clean up old data to prevent database bloat"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        with self.get_session() as db:
            # Clean old news articles (keep only recent ones)
            old_news = db.query(NewsArticle).filter(
                NewsArticle.created_at < cutoff_date
            ).delete()

            # Clean old analyses (but keep some for trending)
            old_analyses = db.query(ContradictionAnalysis).filter(
                ContradictionAnalysis.created_at < cutoff_date
            ).limit(1000).delete()  # Keep some for historical analysis

            # Clean read alerts older than 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            old_alerts = db.query(Alert).filter(
                Alert.created_at < week_ago,
                Alert.is_read == 1
            ).delete()

            db.commit()

            return {
                "deleted_news": old_news,
                "deleted_analyses": old_analyses,
                "deleted_alerts": old_alerts
            }

# Initialize database manager
db_manager = DatabaseManager()