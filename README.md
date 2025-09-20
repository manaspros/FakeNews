# 🕵️ AI Corporate Hypocrisy Detector

A comprehensive real-time system that analyzes corporate promises against actual actions using AI, with a modern React frontend and FastAPI backend.

## 🌟 Features

- **Real-time Analysis**: Gemini AI-powered contradiction detection
- **Live News Monitoring**: Automated news collection from multiple free sources
- **Vector Search**: Free sentence-transformer embeddings with FAISS
- **Real-time Dashboard**: Modern React UI with WebSocket updates
- **Company Management**: Upload documents, track analyses
- **Alert System**: Instant notifications for high-priority contradictions
- **Historical Tracking**: Trend analysis and reporting

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend│───▶│  FastAPI Backend │───▶│   Gemini AI     │
│                 │    │                  │    │                 │
│ • Dashboard     │    │ • REST API       │    │ • Contradiction │
│ • Real-time UI  │    │ • WebSockets     │    │   Analysis      │
│ • Company Mgmt  │    │ • Database       │    │ • Confidence    │
└─────────────────┘    └──────────────────┘    │   Scoring       │
                              │                 └─────────────────┘
                              ▼
                       ┌──────────────────┐
                       │   Data Sources   │
                       │                  │
                       │ • NewsAPI        │
                       │ • RSS Feeds      │
                       │ • File Uploads   │
                       │ • Vector Store   │
                       └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### 1. Clone & Setup
```bash
git clone <repository-url>
cd FakeNews
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and add your API keys:
# GOOGLE_API_KEY=your_gemini_api_key_here
# NEWS_API_KEY=your_news_api_key_here (optional)
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

### 4. Start Everything
```bash
# Option 1: Use the startup script (recommended)
python start.py

# Option 2: Start manually
# Terminal 1 - Backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### 5. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📖 API Keys Setup

### Required APIs
1. **Google Gemini AI** (Primary AI service)
   - Get key from: https://makersuite.google.com/app/apikey
   - Add to `.env`: `GOOGLE_API_KEY=your_key_here`

### Optional APIs (for live news)
2. **NewsAPI** (Free tier: 100 requests/day)
   - Get key from: https://newsapi.org/register
   - Add to `.env`: `NEWS_API_KEY=your_key_here`

3. **NewsData.io** (Free tier: 200 requests/day)
   - Get key from: https://newsdata.io/register
   - Add to `.env`: `NEWSDATA_API_KEY=your_key_here`

> **Note**: The system works without news API keys using RSS feeds and manual news entry.

## 🎯 Usage Guide

### 1. Add Companies
- Go to **Settings** → **Add Company**
- Fill in company details (name, industry, description)
- Upload company documents (ESG reports, codes of conduct)

### 2. Run Analysis
- Go to **Analysis** page
- Select a company
- Choose analysis focus (environmental, employee treatment, etc.)
- Click **Run Analysis** to get contradiction assessment

### 3. Monitor News
- Go to **News** page
- View real-time news for monitored companies
- Add breaking news manually for demo purposes
- Filter by severity level

### 4. View Dashboard
- Real-time overview of all monitored companies
- Active alerts and contradiction levels
- Quick access to analysis and news

## 🔧 Configuration

### Environment Variables
```bash
# AI Service
GOOGLE_API_KEY=your_gemini_api_key

# News APIs (optional)
NEWS_API_KEY=your_news_api_key
NEWSDATA_API_KEY=your_newsdata_key

# Database
DATABASE_URL=sqlite:///./hypocrisy_detector.db

# App Settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Free Alternatives Used
- **AI**: Google Gemini (free tier available)
- **Embeddings**: sentence-transformers (completely free)
- **Vector Store**: FAISS (open source)
- **News**: RSS feeds + NewsAPI free tier
- **Database**: SQLite (file-based, no server needed)

## 📊 Demo Data

The system comes with sample data:
- **TechCorp**: Sample company with ESG report and code of conduct
- **Sample News**: Demo news articles for testing
- **Sample Analyses**: Pre-run contradiction analyses

To reset demo data:
```bash
python backend/document_processor.py
```

## 🎬 Demo Script

### Live Presentation Flow
1. **Show Dashboard**: Overview of monitored companies
2. **Baseline Analysis**: Run analysis on TechCorp environmental practices
3. **Add Breaking News**: Simulate environmental violation news
4. **Live Update**: Watch contradiction level change in real-time
5. **Deep Dive**: Show detailed analysis with specific contradictions

### Sample Breaking News for Demo
```json
{
  "company": "TechCorp",
  "headline": "TechCorp Fined $50M for Illegal Toxic Waste Dumping",
  "content": "EPA investigators found systematic environmental violations...",
  "severity": "HIGH"
}
```

## 🏆 Key Technical Achievements

### Backend Innovations
- **Hybrid AI**: Gemini AI with intelligent fallback detection
- **Free Vector Search**: Sentence-transformers + FAISS for semantic search
- **Multi-source News**: RSS feeds + multiple news APIs
- **Real-time Updates**: WebSocket integration for live alerts
- **Smart Caching**: Optimized for performance and cost

### Frontend Excellence
- **Modern React**: Latest React 19 with hooks and context
- **Real-time UI**: Live updates without page refresh
- **Responsive Design**: Mobile-friendly interface
- **Performance**: Optimized queries and lazy loading
- **UX**: Intuitive workflows and clear data visualization

## 🔍 How It Works

### 1. Document Analysis
- Companies upload ESG reports, codes of conduct, mission statements
- Documents are processed and stored in vector database
- Key promises and commitments are extracted using NLP

### 2. News Monitoring
- System continuously monitors news from multiple sources
- Articles are filtered for relevance to monitored companies
- Severity assessment based on keyword analysis

### 3. Contradiction Detection
- AI compares recent company actions (news) against stated promises (documents)
- Semantic similarity analysis identifies inconsistencies
- Confidence scoring provides reliability metrics

### 4. Real-time Alerts
- High-severity contradictions trigger immediate alerts
- WebSocket updates push notifications to connected users
- Historical tracking shows trends over time

## 🚨 Troubleshooting

### Common Issues

**Backend won't start**
```bash
# Check Python dependencies
pip install -r requirements.txt

# Check port availability
lsof -i :8000  # On macOS/Linux
netstat -ano | findstr :8000  # On Windows
```

**Frontend won't start**
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**No AI responses**
- Check if `GOOGLE_API_KEY` is set in `.env`
- Verify API key is valid at Google AI Studio
- System will use fallback detection if AI fails

**No news data**
- News APIs are optional - system works with RSS feeds
- Check RSS feed connectivity
- Add news manually for testing

## 📈 Performance & Scaling

### Current Capacity
- **Companies**: Unlimited (file-based storage)
- **Documents**: Efficient vector storage
- **News**: Automatic cleanup of old articles
- **Analyses**: Paginated with caching

### Optimization Features
- **Smart Caching**: Reduces API calls and improves response time
- **Batch Processing**: Efficient document and news processing
- **Background Tasks**: Non-blocking news updates
- **Database Cleanup**: Automatic removal of old data

## 🌐 Deployment

### Local Development
Already covered in Quick Start section.

### Production Deployment
```bash
# Backend
gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Frontend
npm run build
# Serve dist/ folder with nginx or similar
```

### Docker (Optional)
```dockerfile
# See docker-compose.yml for full setup
docker-compose up -d
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test
4. Submit pull request

### Code Structure
```
backend/
├── main.py              # FastAPI app
├── ai_service.py        # Gemini AI integration
├── news_service.py      # News collection
├── vector_store.py      # Document embeddings
├── database.py          # SQLite models
└── document_processor.py # PDF/text processing

frontend/src/
├── components/          # Reusable UI components
├── pages/              # Main application pages
├── context/            # React context providers
└── services/           # API integration
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful contradiction analysis
- **Sentence Transformers** for free, high-quality embeddings
- **FAISS** for efficient vector search
- **React & FastAPI** for modern web development
- **Free News Sources** for real-time data

---

**Built for Impact**: This isn't just a demo - it's a production-ready system for corporate accountability in the age of AI.

For questions, issues, or contributions, please open an issue on GitHub.