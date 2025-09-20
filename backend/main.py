from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import json
import logging
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import our services
from backend.ai_service import GeminiAIService, ContradictionResult
from backend.news_service import NewsService, NewsArticle
from backend.vector_store import VectorStore, CompanyDocumentStore
from backend.database import db_manager, get_db
from backend.document_processor import DocumentProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="AI Corporate Hypocrisy Detector",
    description="Real-time analysis of corporate promises vs actions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_service = GeminiAIService()
news_service = NewsService()
vector_store = VectorStore()
doc_store = CompanyDocumentStore(vector_store)
doc_processor = DocumentProcessor()

# Pydantic models
class CompanyRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    industry: Optional[str] = ""
    website: Optional[str] = ""

class AnalysisRequest(BaseModel):
    company: str
    query: Optional[str] = ""

class NewsUpdate(BaseModel):
    company: str
    headline: str
    content: str
    source: str = "Manual"
    severity: str = "MEDIUM"

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Starting AI Corporate Hypocrisy Detector...")

    # Initialize sample data
    await initialize_sample_data()

    logger.info("Application startup complete")

async def initialize_sample_data():
    """Initialize with sample companies and documents"""
    sample_companies = [
        {
            "name": "TechCorp",
            "description": "Global technology company focused on innovation and sustainability",
            "industry": "Technology",
            "website": "https://techcorp.example.com"
        },
        {
            "name": "GreenEnergy Inc",
            "description": "Renewable energy solutions provider",
            "industry": "Energy",
            "website": "https://greenenergy.example.com"
        },
        {
            "name": "GlobalBank",
            "description": "International banking and financial services",
            "industry": "Finance",
            "website": "https://globalbank.example.com"
        }
    ]

    for company_data in sample_companies:
        db_manager.add_company(**company_data)

    # Add sample documents to vector store
    await add_sample_documents()

async def add_sample_documents():
    """Add sample company documents"""
    sample_docs = [
        (
            "TechCorp",
            "ESG Report",
            """TechCorp Environmental, Social & Governance Report 2024

            Environmental Commitments:
            - Achieve carbon neutrality by 2030 across all operations
            - Reduce water usage by 50% by 2025
            - Zero waste to landfill by 2027
            - Invest $1 billion in renewable energy projects

            Social Responsibility:
            - Maintain diverse and inclusive workplace
            - Ensure equal pay for equal work
            - Provide safe working conditions for all employees
            - Support local communities through volunteer programs

            Governance Principles:
            - Transparent reporting of all business practices
            - Ethical treatment of suppliers and partners
            - Regular compliance audits and assessments
            """
        ),
        (
            "GreenEnergy Inc",
            "Mission Statement",
            """GreenEnergy Inc Mission and Values

            Our Mission: To accelerate the world's transition to sustainable energy

            Core Values:
            - Environmental stewardship and protection
            - Innovation in clean technology solutions
            - Fair treatment of all stakeholders
            - Transparency in all business operations
            - Community engagement and support

            Commitments:
            - 100% renewable energy in all facilities by 2025
            - Zero carbon emissions by 2030
            - Ethical sourcing of all materials
            - Fair wages and benefits for all employees
            """
        ),
        (
            "GlobalBank",
            "Code of Conduct",
            """GlobalBank Code of Conduct

            Ethical Banking Principles:
            - Honest and transparent customer relationships
            - Responsible lending practices
            - Protection of customer data and privacy
            - Compliance with all financial regulations

            Employee Standards:
            - Respect and dignity for all employees
            - Zero tolerance for discrimination or harassment
            - Fair compensation and career development
            - Safe and healthy work environment

            Community Responsibility:
            - Support for local economic development
            - Financial literacy education programs
            - Environmental protection initiatives
            - Charitable giving and volunteer activities
            """
        )
    ]

    for company, doc_type, content in sample_docs:
        # Add to database
        db_manager.add_company_document(
            company_name=company,
            doc_type=doc_type,
            title=f"{company} {doc_type}",
            content=content
        )

        # Add to vector store
        doc_store.add_company_document(company, doc_type, content)

    # Save vector store
    vector_store.save_index()

# API Routes

@app.get("/")
async def root():
    return {"message": "AI Corporate Hypocrisy Detector API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "ai_service": ai_service.gemini_enabled,
            "vector_store": len(vector_store.documents) > 0,
            "database": True
        }
    }

@app.get("/companies")
async def get_companies():
    """Get list of all companies"""
    companies = db_manager.get_companies()
    return [{"name": c.name, "description": c.description, "industry": c.industry} for c in companies]

@app.post("/companies")
async def add_company(company: CompanyRequest):
    """Add a new company"""
    try:
        db_company = db_manager.add_company(
            name=company.name,
            description=company.description,
            industry=company.industry,
            website=company.website
        )
        return {"message": "Company added successfully", "company": company.name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/companies/{company_name}/stats")
async def get_company_stats(company_name: str):
    """Get statistics for a specific company"""
    return db_manager.get_company_stats(company_name)

@app.get("/debug/analysis-data/{company_name}")
async def debug_analysis_data(company_name: str, query: str = ""):
    """Debug endpoint to see what data is being used for analysis"""
    try:
        # Get company promises from vector store
        promises = doc_store.get_company_promises(company_name, query)
        promises_text = "\n".join([p['content'] for p in promises])

        # Get recent news
        news_articles = db_manager.get_recent_news(company_name, limit=10)
        actions_text = "\n".join([f"{a.title}: {a.content}" for a in news_articles])

        return {
            "company": company_name,
            "query": query,
            "promises_count": len(promises),
            "news_count": len(news_articles),
            "promises_text_length": len(promises_text),
            "actions_text_length": len(actions_text),
            "promises_preview": promises_text[:500] if promises_text else "No promises found",
            "actions_preview": actions_text[:500] if actions_text else "No actions found",
            "promises_full": promises_text if len(promises_text) < 1000 else promises_text[:1000] + "...",
            "actions_full": actions_text if len(actions_text) < 1000 else actions_text[:1000] + "..."
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze")
async def analyze_company(request: AnalysisRequest):
    """Analyze a company for contradictions"""
    try:
        # Get company promises from vector store
        promises = doc_store.get_company_promises(request.company, request.query)
        promises_text = "\n".join([p['content'] for p in promises])

        # Get recent news
        news_articles = db_manager.get_recent_news(request.company, limit=10)
        actions_text = "\n".join([f"{a.title}: {a.content}" for a in news_articles])

        # Debug logging
        logger.info(f"Analysis for {request.company}:")
        logger.info(f"Found {len(promises)} promise documents, {len(news_articles)} news articles")
        logger.info(f"Promises text length: {len(promises_text)}")
        logger.info(f"Actions text length: {len(actions_text)}")
        if len(promises_text) > 0:
            logger.info(f"Promises preview: {promises_text[:200]}...")
        if len(actions_text) > 0:
            logger.info(f"Actions preview: {actions_text[:200]}...")

        # Perform AI analysis
        result = ai_service.analyze_contradiction(
            company=request.company,
            query=request.query,
            promises=promises_text,
            actions=actions_text
        )

        # Save analysis to database
        analysis_data = {
            "company_name": request.company,
            "query": request.query,
            "contradiction_level": result.contradiction_level,
            "confidence_score": result.confidence_score,
            "analysis": result.analysis,
            "promises_excerpt": result.promises_excerpt,
            "actions_excerpt": result.actions_excerpt,
            "key_contradictions": result.key_contradictions
        }
        db_manager.add_contradiction_analysis(analysis_data)

        # Create alert if high contradiction
        if result.contradiction_level in ["HIGH", "MEDIUM"]:
            db_manager.add_alert(
                company_name=request.company,
                alert_type="CONTRADICTION",
                level=result.contradiction_level,
                title=f"Contradiction detected for {request.company}",
                message=f"Analysis found {result.contradiction_level} level contradictions",
                data={"analysis_id": result.timestamp}
            )

            # Broadcast alert via WebSocket
            await manager.broadcast(json.dumps({
                "type": "alert",
                "company": request.company,
                "level": result.contradiction_level,
                "message": f"New contradiction detected for {request.company}"
            }))

        return {
            "company": result.company,
            "query": result.query,
            "contradiction_level": result.contradiction_level,
            "confidence_score": result.confidence_score,
            "analysis": result.analysis,
            "key_contradictions": result.key_contradictions,
            "timestamp": result.timestamp
        }

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/companies/{company_name}/news")
async def get_company_news(company_name: str, limit: int = 20):
    """Get recent news for a company"""
    try:
        # Try to fetch fresh news
        fresh_news = await news_service.fetch_company_news(company_name, days_back=7)

        # Save fresh news to database
        for article in fresh_news[:10]:  # Limit to avoid spam
            article_data = {
                "company_name": company_name,
                "title": article.title,
                "content": article.content,
                "url": article.url,
                "source": article.source,
                "published_at": article.published_at,
                "sentiment_score": article.sentiment_score,
                "relevance_score": article.relevance_score,
                "severity": article.severity,
                "keywords": article.keywords
            }
            db_manager.add_news_article(article_data)

        # Get news from database
        db_news = db_manager.get_recent_news(company_name, limit)

        return [{
            "id": article.id,
            "title": article.title,
            "content": article.content[:500] + "..." if len(article.content) > 500 else article.content,
            "url": article.url,
            "source": article.source,
            "published_at": article.published_at.isoformat(),
            "sentiment_score": article.sentiment_score,
            "severity": article.severity
        } for article in db_news]

    except Exception as e:
        logger.error(f"News fetch error: {e}")
        # Fallback to database only
        db_news = db_manager.get_recent_news(company_name, limit)
        return [{"id": a.id, "title": a.title, "source": a.source} for a in db_news]

@app.post("/news")
async def add_news_update(update: NewsUpdate):
    """Manually add a news update (for demo purposes)"""
    try:
        article_data = {
            "company_name": update.company,
            "title": update.headline,
            "content": update.content,
            "url": "",
            "source": update.source,
            "published_at": datetime.utcnow(),
            "sentiment_score": 0.0,
            "relevance_score": 1.0,
            "severity": update.severity,
            "keywords": []
        }

        article = db_manager.add_news_article(article_data)

        # Broadcast news update via WebSocket
        await manager.broadcast(json.dumps({
            "type": "news_update",
            "company": update.company,
            "headline": update.headline,
            "severity": update.severity
        }))

        return {"message": "News update added successfully", "id": article.id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/companies/{company_name}/analyses")
async def get_company_analyses(company_name: str, limit: int = 10):
    """Get recent analyses for a company"""
    analyses = db_manager.get_recent_analyses(company_name, limit)

    return [{
        "id": analysis.id,
        "query": analysis.query,
        "contradiction_level": analysis.contradiction_level,
        "confidence_score": analysis.confidence_score,
        "analysis": analysis.analysis[:500] + "..." if len(analysis.analysis) > 500 else analysis.analysis,
        "created_at": analysis.created_at.isoformat()
    } for analysis in analyses]

@app.get("/alerts")
async def get_alerts(company_name: Optional[str] = None):
    """Get unread alerts"""
    alerts = db_manager.get_unread_alerts(company_name)

    return [{
        "id": alert.id,
        "company_name": alert.company_name,
        "alert_type": alert.alert_type,
        "level": alert.level,
        "title": alert.title,
        "message": alert.message,
        "created_at": alert.created_at.isoformat()
    } for alert in alerts]

@app.post("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: int):
    """Mark an alert as read"""
    db_manager.mark_alert_read(alert_id)
    return {"message": "Alert marked as read"}

@app.post("/upload-document")
async def upload_document(
    company: str = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload a company document"""
    try:
        # Save uploaded file
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)

        file_path = upload_dir / f"{company}_{doc_type}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process document
        if file.filename.endswith('.pdf'):
            content = doc_processor.extract_pdf_content(str(file_path))
        else:
            content = content.decode('utf-8')

        # Add to database and vector store
        db_manager.add_company_document(
            company_name=company,
            doc_type=doc_type,
            title=file.filename,
            content=content,
            file_path=str(file_path)
        )

        doc_store.add_company_document(company, doc_type, content, str(file_path))
        vector_store.save_index()

        return {"message": "Document uploaded and processed successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back or handle specific commands
            await manager.send_personal_message(f"Received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task for periodic news updates
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(periodic_news_update())

async def periodic_news_update():
    """Periodically fetch news for all companies"""
    while True:
        try:
            companies = db_manager.get_companies()
            for company in companies:
                # Fetch news for each company
                news = await news_service.fetch_company_news(company.name, days_back=1)

                # Save new articles
                for article in news[:5]:  # Limit to avoid spam
                    article_data = {
                        "company_name": company.name,
                        "title": article.title,
                        "content": article.content,
                        "url": article.url,
                        "source": article.source,
                        "published_at": article.published_at,
                        "sentiment_score": article.sentiment_score,
                        "relevance_score": article.relevance_score,
                        "severity": article.severity,
                        "keywords": article.keywords
                    }
                    db_manager.add_news_article(article_data)

            logger.info("Completed periodic news update")

        except Exception as e:
            logger.error(f"Periodic news update error: {e}")

        # Wait 1 hour before next update
        await asyncio.sleep(3600)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )