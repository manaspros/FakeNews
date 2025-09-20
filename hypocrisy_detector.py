import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import time
from document_processor import DocumentProcessor
from news_monitor import NewsMonitor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI not available. Install with: pip install openai")

@dataclass
class ContradictionResult:
    company: str
    query: str
    contradiction_level: str  # LOW, MEDIUM, HIGH
    confidence_score: float
    analysis: str
    promises_excerpt: str
    actions_excerpt: str
    timestamp: int

class HypocrisyDetector:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.news_monitor = NewsMonitor()

        # Initialize OpenAI client if available
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.openai_enabled = True
        else:
            self.client = None
            self.openai_enabled = False
            print("⚠️ OpenAI not configured. Using fallback detection.")

        # Cache for analysis results
        self.analysis_cache = {}

    def analyze_company(self, company_id: str, query: str = "") -> ContradictionResult:
        """Main method to analyze a company for contradictions"""

        # Get company promises from documents
        promises = self.document_processor.get_company_promises(
            company_id,
            keywords=self._extract_keywords(query) if query else None
        )

        # Get recent company news/actions
        recent_news = self.news_monitor.get_company_news(company_id, hours_back=168)  # 1 week
        actions = self._format_news_for_analysis(recent_news)

        if not promises and not actions:
            return ContradictionResult(
                company=company_id,
                query=query,
                contradiction_level="UNKNOWN",
                confidence_score=0.0,
                analysis="No data available for analysis",
                promises_excerpt="No promises found",
                actions_excerpt="No recent actions found",
                timestamp=int(time.time())
            )

        # Perform contradiction analysis
        if self.openai_enabled:
            result = self._analyze_with_openai(company_id, query, promises, actions)
        else:
            result = self._analyze_with_fallback(company_id, query, promises, actions)

        return result

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract relevant keywords from user query"""
        # Simple keyword extraction (can be enhanced)
        common_themes = {
            'environment': ['environmental', 'climate', 'carbon', 'green', 'sustainability', 'pollution'],
            'employee': ['employee', 'worker', 'staff', 'diversity', 'inclusion', 'workplace'],
            'ethics': ['ethical', 'integrity', 'honest', 'transparent', 'corruption'],
            'social': ['community', 'social', 'charity', 'volunteer', 'giving']
        }

        query_lower = query.lower()
        keywords = []

        for theme, theme_keywords in common_themes.items():
            if any(word in query_lower for word in theme_keywords):
                keywords.extend(theme_keywords)

        return keywords if keywords else ['commitment', 'promise', 'value']

    def _format_news_for_analysis(self, news_items: List[Dict]) -> str:
        """Format news items for analysis"""
        if not news_items:
            return "No recent news found"

        formatted = []
        for item in news_items[:5]:  # Top 5 most recent
            formatted.append(
                f"[{item.get('source', 'Unknown')}] {item.get('headline', '')}\n"
                f"{item.get('content', '')}\n"
            )

        return "\n".join(formatted)

    def _analyze_with_openai(self, company_id: str, query: str, promises: str, actions: str) -> ContradictionResult:
        """Analyze contradictions using OpenAI"""

        system_prompt = """You are an expert corporate analyst specializing in identifying contradictions between company statements and actions. Your job is to objectively assess whether a company's recent actions contradict their stated commitments and values.

For each analysis:
1. Compare the company's official promises/commitments with their recent actions
2. Identify any clear contradictions or inconsistencies
3. Rate the contradiction level as HIGH, MEDIUM, LOW, or NONE
4. Provide confidence score (0.0 to 1.0)
5. Give specific examples and explain your reasoning

Be objective and evidence-based. Don't assume malicious intent, but be thorough in identifying genuine contradictions."""

        user_prompt = f"""Analyze {company_id} for contradictions between promises and actions:

QUERY FOCUS: {query if query else "General corporate behavior"}

OFFICIAL COMPANY COMMITMENTS:
{promises}

RECENT COMPANY ACTIONS:
{actions}

Please provide:
1. Contradiction level (NONE/LOW/MEDIUM/HIGH)
2. Confidence score (0.0-1.0)
3. Detailed analysis explaining any contradictions found
4. Specific examples from the evidence provided

Format your response as JSON:
{{
    "contradiction_level": "HIGH/MEDIUM/LOW/NONE",
    "confidence_score": 0.85,
    "analysis": "Detailed explanation...",
    "key_contradictions": ["contradiction 1", "contradiction 2"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            # Parse response
            response_text = response.choices[0].message.content

            # Try to extract JSON from response
            try:
                # Find JSON in response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    result_data = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")

            except (json.JSONDecodeError, ValueError):
                # Fallback: parse response manually
                result_data = self._parse_openai_response(response_text)

            return ContradictionResult(
                company=company_id,
                query=query,
                contradiction_level=result_data.get('contradiction_level', 'UNKNOWN'),
                confidence_score=result_data.get('confidence_score', 0.5),
                analysis=result_data.get('analysis', response_text),
                promises_excerpt=promises[:500] + "..." if len(promises) > 500 else promises,
                actions_excerpt=actions[:500] + "..." if len(actions) > 500 else actions,
                timestamp=int(time.time())
            )

        except Exception as e:
            print(f"OpenAI analysis failed: {e}")
            return self._analyze_with_fallback(company_id, query, promises, actions)

    def _parse_openai_response(self, response: str) -> Dict:
        """Fallback parser for OpenAI response"""
        # Simple keyword-based parsing
        response_lower = response.lower()

        # Determine contradiction level
        if 'high' in response_lower and 'contradiction' in response_lower:
            level = 'HIGH'
            confidence = 0.8
        elif 'medium' in response_lower and 'contradiction' in response_lower:
            level = 'MEDIUM'
            confidence = 0.6
        elif 'low' in response_lower and 'contradiction' in response_lower:
            level = 'LOW'
            confidence = 0.4
        else:
            level = 'NONE'
            confidence = 0.2

        return {
            'contradiction_level': level,
            'confidence_score': confidence,
            'analysis': response
        }

    def _analyze_with_fallback(self, company_id: str, query: str, promises: str, actions: str) -> ContradictionResult:
        """Simple rule-based fallback analysis"""

        # Keywords indicating potential contradictions
        negative_keywords = [
            'lawsuit', 'fine', 'penalty', 'scandal', 'violation', 'illegal',
            'layoffs', 'discrimination', 'pollution', 'breach', 'fraud'
        ]

        positive_keywords = [
            'commitment', 'pledge', 'promise', 'value', 'ethical', 'responsible',
            'sustainable', 'inclusive', 'transparent'
        ]

        actions_lower = actions.lower()
        promises_lower = promises.lower()

        # Count negative signals in actions
        negative_signals = sum(1 for keyword in negative_keywords if keyword in actions_lower)

        # Count positive signals in promises
        positive_signals = sum(1 for keyword in positive_keywords if keyword in promises_lower)

        # Simple contradiction scoring
        if negative_signals > 0 and positive_signals > 0:
            if negative_signals >= 3:
                level = "HIGH"
                confidence = 0.7
                analysis = f"Detected {negative_signals} concerning actions against {positive_signals} positive commitments. Significant contradiction likely."
            elif negative_signals >= 2:
                level = "MEDIUM"
                confidence = 0.5
                analysis = f"Detected {negative_signals} concerning actions against {positive_signals} positive commitments. Moderate contradiction possible."
            else:
                level = "LOW"
                confidence = 0.3
                analysis = f"Detected {negative_signals} concerning actions against {positive_signals} positive commitments. Minor contradiction possible."
        else:
            level = "NONE"
            confidence = 0.2
            analysis = "No clear contradictions detected with available data."

        return ContradictionResult(
            company=company_id,
            query=query,
            contradiction_level=level,
            confidence_score=confidence,
            analysis=analysis,
            promises_excerpt=promises[:500] + "..." if len(promises) > 500 else promises,
            actions_excerpt=actions[:500] + "..." if len(actions) > 500 else actions,
            timestamp=int(time.time())
        )

    def setup_demo_data(self):
        """Setup demo data for presentation"""
        # Create sample documents
        self.document_processor.create_sample_documents()

        # Create sample news
        self.news_monitor.create_sample_news()

        print("✅ Demo data setup complete!")

if __name__ == "__main__":
    # Demo usage
    detector = HypocrisyDetector()
    detector.setup_demo_data()

    # Analyze TechCorp
    result = detector.analyze_company("TechCorp", "employee treatment")

    print(f"\n🔍 Analysis Results for TechCorp:")
    print(f"Contradiction Level: {result.contradiction_level}")
    print(f"Confidence: {result.confidence_score:.2f}")
    print(f"Analysis: {result.analysis}")