import os
import google.generativeai as genai
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import time
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging
from dotenv import load_dotenv

# Environment variables are loaded in main.py

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContradictionResult:
    company: str
    query: str
    contradiction_level: str  # NONE, LOW, MEDIUM, HIGH
    confidence_score: float
    analysis: str
    promises_excerpt: str
    actions_excerpt: str
    key_contradictions: List[str]
    timestamp: int

class GeminiAIService:
    def __init__(self):
        self.setup_gemini()
        self.setup_embeddings()

    def setup_gemini(self):
        """Initialize Gemini API"""
        api_key = os.getenv('GOOGLE_API_KEY')
        logger.info(f"Checking for Gemini API key... Found: {bool(api_key)}")
        if not api_key:
            logger.warning("No Gemini API key found. Using fallback analysis.")
            self.gemini_enabled = False
            return

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.gemini_enabled = True
            logger.info("Gemini API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.gemini_enabled = False

    def setup_embeddings(self):
        """Initialize free embedding model"""
        try:
            # Using sentence-transformers with a free model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts"""
        if not self.embedding_model:
            # Fallback: simple word counting vectors
            return self._simple_embeddings(texts)

        try:
            return self.embedding_model.encode(texts)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return self._simple_embeddings(texts)

    def _simple_embeddings(self, texts: List[str]) -> np.ndarray:
        """Fallback embedding method using word frequencies"""
        from collections import Counter
        import re

        # Create vocabulary from all texts
        all_words = set()
        processed_texts = []

        for text in texts:
            words = re.findall(r'\w+', text.lower())
            processed_texts.append(words)
            all_words.update(words)

        vocab = list(all_words)
        embeddings = []

        for words in processed_texts:
            word_counts = Counter(words)
            vector = [word_counts.get(word, 0) for word in vocab]
            embeddings.append(vector)

        return np.array(embeddings)

    def analyze_contradiction(self, company: str, query: str, promises: str, actions: str) -> ContradictionResult:
        """Main contradiction analysis method"""

        if self.gemini_enabled:
            try:
                return self._analyze_with_gemini(company, query, promises, actions)
            except Exception as e:
                logger.error(f"Gemini analysis failed: {e}")
                return self._analyze_with_fallback(company, query, promises, actions)
        else:
            return self._analyze_with_fallback(company, query, promises, actions)

    def _analyze_with_gemini(self, company: str, query: str, promises: str, actions: str) -> ContradictionResult:
        """Analyze contradictions using Gemini"""

        system_prompt = """You are an expert corporate analyst specializing in identifying contradictions between company statements and actions.

Your task is to:
1. Objectively compare company promises/commitments with recent actions
2. Identify contradictions or inconsistencies
3. Rate contradiction level: NONE, LOW, MEDIUM, HIGH
4. Provide confidence score (0.0 to 1.0)
5. List specific contradictions found
6. Be evidence-based and cite specific examples

Respond ONLY with valid JSON in this exact format:
{
    "contradiction_level": "HIGH",
    "confidence_score": 0.85,
    "analysis": "Detailed explanation of contradictions found...",
    "key_contradictions": ["contradiction 1", "contradiction 2"]
}"""

        user_prompt = f"""Company: {company}
Query Focus: {query if query else "General corporate behavior"}

OFFICIAL COMMITMENTS:
{promises}

RECENT ACTIONS:
{actions}

Analyze for contradictions between stated values and actual behavior."""

        try:
            # Combine system and user prompts for Gemini
            full_prompt = f"{system_prompt}\n\n{user_prompt}"

            response = self.model.generate_content(full_prompt)
            response_text = response.text

            # Extract JSON from response
            result_data = self._extract_json_from_response(response_text)

            return ContradictionResult(
                company=company,
                query=query,
                contradiction_level=result_data.get('contradiction_level', 'UNKNOWN'),
                confidence_score=float(result_data.get('confidence_score', 0.5)),
                analysis=result_data.get('analysis', response_text),
                promises_excerpt=self._truncate_text(promises, 500),
                actions_excerpt=self._truncate_text(actions, 500),
                key_contradictions=result_data.get('key_contradictions', []),
                timestamp=int(time.time())
            )

        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
            raise e

    def _extract_json_from_response(self, response_text: str) -> Dict:
        """Extract JSON from Gemini response"""
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return self._parse_response_fallback(response_text)

        except json.JSONDecodeError:
            return self._parse_response_fallback(response_text)

    def _parse_response_fallback(self, response: str) -> Dict:
        """Fallback parser for non-JSON responses"""
        response_lower = response.lower()

        # Determine contradiction level
        if 'high' in response_lower and ('contradiction' in response_lower or 'severe' in response_lower):
            level = 'HIGH'
            confidence = 0.8
        elif 'medium' in response_lower and 'contradiction' in response_lower:
            level = 'MEDIUM'
            confidence = 0.6
        elif 'low' in response_lower and 'contradiction' in response_lower:
            level = 'LOW'
            confidence = 0.4
        elif 'none' in response_lower or 'no contradiction' in response_lower:
            level = 'NONE'
            confidence = 0.2
        else:
            level = 'UNKNOWN'
            confidence = 0.3

        # Extract key points as contradictions
        contradictions = []
        sentences = response.split('.')
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['contradict', 'inconsistent', 'violate', 'breach']):
                contradictions.append(sentence.strip())

        return {
            'contradiction_level': level,
            'confidence_score': confidence,
            'analysis': response,
            'key_contradictions': contradictions[:3]  # Top 3
        }

    def _analyze_with_fallback(self, company: str, query: str, promises: str, actions: str) -> ContradictionResult:
        """Enhanced fallback analysis using embeddings and rule-based detection"""

        # Rule-based analysis
        negative_keywords = [
            'lawsuit', 'fine', 'penalty', 'scandal', 'violation', 'illegal',
            'layoffs', 'discrimination', 'pollution', 'breach', 'fraud',
            'investigation', 'charges', 'misconduct', 'abuse', 'exploit'
        ]

        positive_keywords = [
            'commitment', 'pledge', 'promise', 'value', 'ethical', 'responsible',
            'sustainable', 'inclusive', 'transparent', 'integrity', 'compliance'
        ]

        actions_lower = actions.lower()
        promises_lower = promises.lower()

        # Count signals
        negative_signals = sum(1 for keyword in negative_keywords if keyword in actions_lower)
        positive_signals = sum(1 for keyword in positive_keywords if keyword in promises_lower)

        # Semantic similarity analysis
        similarity_score = 0.5
        if self.embedding_model and promises and actions:
            try:
                promise_embedding = self.get_embeddings([promises])
                action_embedding = self.get_embeddings([actions])
                similarity_score = cosine_similarity(promise_embedding, action_embedding)[0][0]
            except Exception as e:
                logger.error(f"Similarity calculation failed: {e}")

        # Calculate contradiction level
        contradiction_score = self._calculate_contradiction_score(
            negative_signals, positive_signals, similarity_score
        )

        level, confidence, analysis = self._interpret_contradiction_score(
            contradiction_score, negative_signals, positive_signals, similarity_score
        )

        # Extract key contradictions
        key_contradictions = []
        for keyword in negative_keywords:
            if keyword in actions_lower:
                key_contradictions.append(f"Actions show evidence of: {keyword}")
                if len(key_contradictions) >= 3:
                    break

        return ContradictionResult(
            company=company,
            query=query,
            contradiction_level=level,
            confidence_score=float(confidence),
            analysis=analysis,
            promises_excerpt=self._truncate_text(promises, 500),
            actions_excerpt=self._truncate_text(actions, 500),
            key_contradictions=key_contradictions,
            timestamp=int(time.time())
        )

    def _calculate_contradiction_score(self, negative_signals: int, positive_signals: int, similarity: float) -> float:
        """Calculate overall contradiction score"""
        # Base score from keyword analysis
        keyword_score = min(negative_signals / max(positive_signals, 1), 2.0)

        # Semantic contradiction (low similarity = high contradiction)
        semantic_score = 1.0 - similarity

        # Combined score
        combined_score = (keyword_score * 0.7) + (semantic_score * 0.3)

        return min(combined_score, 1.0)

    def _interpret_contradiction_score(self, score: float, negative: int, positive: int, similarity: float) -> tuple:
        """Interpret contradiction score into level, confidence, and analysis"""

        if score >= 0.7:
            level = "HIGH"
            confidence = min(0.9, 0.6 + score * 0.3)
            analysis = f"Significant contradictions detected. Found {negative} concerning actions against {positive} positive commitments. Semantic similarity: {similarity:.2f}"
        elif score >= 0.4:
            level = "MEDIUM"
            confidence = min(0.8, 0.4 + score * 0.3)
            analysis = f"Moderate contradictions possible. Found {negative} concerning actions against {positive} positive commitments. Semantic similarity: {similarity:.2f}"
        elif score >= 0.2:
            level = "LOW"
            confidence = min(0.6, 0.3 + score * 0.3)
            analysis = f"Minor contradictions detected. Found {negative} concerning actions against {positive} positive commitments. Semantic similarity: {similarity:.2f}"
        else:
            level = "NONE"
            confidence = min(0.7, 0.2 + (1.0 - score) * 0.3)
            analysis = f"No significant contradictions detected. Actions appear consistent with stated commitments. Semantic similarity: {similarity:.2f}"

        return level, confidence, analysis

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length"""
        if not text:
            return ""
        return text[:max_length] + "..." if len(text) > max_length else text

    def get_contradiction_summary(self, results: List[ContradictionResult]) -> Dict:
        """Generate summary of multiple contradiction analyses"""
        if not results:
            return {"overall_score": 0, "risk_level": "UNKNOWN", "summary": "No data available"}

        # Calculate overall risk score
        level_weights = {"NONE": 0, "LOW": 0.25, "MEDIUM": 0.5, "HIGH": 1.0}
        total_score = sum(
            level_weights.get(result.contradiction_level, 0) * result.confidence_score
            for result in results
        )
        overall_score = total_score / len(results)

        # Determine overall risk level
        if overall_score >= 0.7:
            risk_level = "HIGH"
        elif overall_score >= 0.4:
            risk_level = "MEDIUM"
        elif overall_score >= 0.2:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"

        # Generate summary
        high_count = sum(1 for r in results if r.contradiction_level == "HIGH")
        medium_count = sum(1 for r in results if r.contradiction_level == "MEDIUM")

        summary = f"Analysis of {len(results)} areas found {high_count} high-risk and {medium_count} medium-risk contradictions."

        return {
            "overall_score": round(overall_score, 2),
            "risk_level": risk_level,
            "summary": summary,
            "total_analyses": len(results),
            "high_risk_count": high_count,
            "medium_risk_count": medium_count
        }