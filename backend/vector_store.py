import os
import numpy as np
import faiss
import pickle
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from sentence_transformers import SentenceTransformer
import json
import hashlib
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Document:
    id: str
    content: str
    metadata: Dict
    embedding: Optional[np.ndarray] = None

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'metadata': self.metadata
            # Note: embedding excluded from dict for JSON serialization
        }

class VectorStore:
    def __init__(self, dimension: int = 384, index_file: str = "vector_index.faiss"):
        self.dimension = dimension
        self.index_file = index_file
        self.metadata_file = index_file.replace('.faiss', '_metadata.json')

        # Initialize embedding model (free alternative to OpenAI)
        self.embedding_model = self._load_embedding_model()

        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.documents = {}  # id -> Document mapping
        self.id_to_index = {}  # id -> faiss index mapping

        # Load existing index if available
        self._load_index()

    def _load_embedding_model(self):
        """Load free sentence transformer model"""
        try:
            # Using all-MiniLM-L6-v2: 384 dimensions, good performance, fast
            model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded sentence transformer model: all-MiniLM-L6-v2")
            return model
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            # Fallback to even smaller model
            try:
                model = SentenceTransformer('all-MiniLM-L12-v2')
                logger.info("Loaded fallback model: all-MiniLM-L12-v2")
                return model
            except Exception as e2:
                logger.error(f"Failed to load fallback model: {e2}")
                return None

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if not self.embedding_model:
            return self._simple_embedding(text)

        try:
            embedding = self.embedding_model.encode(text, normalize_embeddings=True)
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return self._simple_embedding(text)

    def _simple_embedding(self, text: str) -> np.ndarray:
        """Fallback simple embedding using TF-IDF like approach"""
        # This is a very basic fallback - in production you'd want a better alternative
        words = text.lower().split()

        # Create a simple hash-based embedding
        embedding = np.zeros(self.dimension)

        for i, word in enumerate(words[:50]):  # Limit to first 50 words
            # Simple hash to index mapping
            hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
            idx = hash_val % self.dimension
            embedding[idx] += 1.0 / (i + 1)  # Weight by position

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding.astype(np.float32)

    def add_document(self, doc_id: str, content: str, metadata: Dict) -> str:
        """Add a document to the vector store"""
        try:
            # Generate embedding
            embedding = self.embed_text(content)

            # Create document
            document = Document(
                id=doc_id,
                content=content,
                metadata=metadata,
                embedding=embedding
            )

            # Add to FAISS index
            index_id = self.index.ntotal
            self.index.add(embedding.reshape(1, -1))

            # Store mappings
            self.documents[doc_id] = document
            self.id_to_index[doc_id] = index_id

            logger.info(f"Added document {doc_id} to vector store")
            return doc_id

        except Exception as e:
            logger.error(f"Failed to add document {doc_id}: {e}")
            raise e

    def add_documents(self, documents: List[Tuple[str, str, Dict]]) -> List[str]:
        """Add multiple documents at once"""
        doc_ids = []

        for doc_id, content, metadata in documents:
            try:
                added_id = self.add_document(doc_id, content, metadata)
                doc_ids.append(added_id)
            except Exception as e:
                logger.error(f"Failed to add document {doc_id}: {e}")

        return doc_ids

    def search(self, query: str, k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """Search for similar documents"""
        try:
            # Generate query embedding
            query_embedding = self.embed_text(query)

            # Search in FAISS
            scores, indices = self.index.search(query_embedding.reshape(1, -1), min(k * 2, self.index.ntotal))

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # FAISS returns -1 for empty slots
                    continue

                # Find document by index
                doc_id = None
                for did, doc_idx in self.id_to_index.items():
                    if doc_idx == idx:
                        doc_id = did
                        break

                if doc_id and doc_id in self.documents:
                    document = self.documents[doc_id]

                    # Apply metadata filter if provided
                    if filter_metadata:
                        if not self._matches_filter(document.metadata, filter_metadata):
                            continue

                    result = {
                        'id': document.id,
                        'content': document.content,
                        'metadata': document.metadata,
                        'score': float(score)
                    }
                    results.append(result)

                    if len(results) >= k:
                        break

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def _matches_filter(self, metadata: Dict, filter_metadata: Dict) -> bool:
        """Check if metadata matches filter criteria"""
        for key, value in filter_metadata.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get document by ID"""
        return self.documents.get(doc_id)

    def update_document(self, doc_id: str, content: str = None, metadata: Dict = None):
        """Update an existing document"""
        if doc_id not in self.documents:
            raise ValueError(f"Document {doc_id} not found")

        document = self.documents[doc_id]

        # Update content if provided
        if content is not None:
            document.content = content
            # Regenerate embedding
            document.embedding = self.embed_text(content)

            # Update in FAISS index
            index_id = self.id_to_index[doc_id]
            # Note: FAISS doesn't support in-place updates easily
            # For simplicity, we'll rebuild the index if needed

        # Update metadata if provided
        if metadata is not None:
            document.metadata.update(metadata)

        logger.info(f"Updated document {doc_id}")

    def delete_document(self, doc_id: str):
        """Delete a document (mark as deleted)"""
        if doc_id in self.documents:
            # For simplicity, just remove from our mappings
            # FAISS index will still contain the embedding but it won't be found
            del self.documents[doc_id]
            if doc_id in self.id_to_index:
                del self.id_to_index[doc_id]
            logger.info(f"Deleted document {doc_id}")

    def save_index(self):
        """Save the index and metadata to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_file)

            # Save metadata and mappings
            metadata_to_save = {
                'documents': {doc_id: doc.to_dict() for doc_id, doc in self.documents.items()},
                'id_to_index': self.id_to_index
            }

            with open(self.metadata_file, 'w') as f:
                json.dump(metadata_to_save, f, indent=2)

            logger.info(f"Saved vector store to {self.index_file}")

        except Exception as e:
            logger.error(f"Failed to save index: {e}")

    def _load_index(self):
        """Load existing index from disk"""
        try:
            if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
                # Load FAISS index
                self.index = faiss.read_index(self.index_file)

                # Load metadata
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)

                # Reconstruct documents (without embeddings for now)
                self.documents = {}
                for doc_id, doc_data in metadata['documents'].items():
                    document = Document(
                        id=doc_data['id'],
                        content=doc_data['content'],
                        metadata=doc_data['metadata']
                    )
                    self.documents[doc_id] = document

                self.id_to_index = metadata['id_to_index']

                logger.info(f"Loaded vector store from {self.index_file}")
                logger.info(f"Index contains {self.index.ntotal} vectors")

        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            # Initialize empty index
            self.index = faiss.IndexFlatIP(self.dimension)

    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        return {
            'total_documents': len(self.documents),
            'index_size': self.index.ntotal,
            'dimension': self.dimension,
            'companies': list(set(doc.metadata.get('company', 'Unknown') for doc in self.documents.values())),
            'document_types': list(set(doc.metadata.get('type', 'Unknown') for doc in self.documents.values()))
        }

    def rebuild_index(self):
        """Rebuild the FAISS index from scratch"""
        logger.info("Rebuilding FAISS index...")

        # Create new index
        new_index = faiss.IndexFlatIP(self.dimension)
        new_id_to_index = {}

        # Add all documents back
        for doc_id, document in self.documents.items():
            if document.embedding is None:
                document.embedding = self.embed_text(document.content)

            index_id = new_index.ntotal
            new_index.add(document.embedding.reshape(1, -1))
            new_id_to_index[doc_id] = index_id

        # Replace old index
        self.index = new_index
        self.id_to_index = new_id_to_index

        logger.info("Index rebuild complete")


class CompanyDocumentStore:
    """Specialized store for company documents"""

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def add_company_document(self, company: str, doc_type: str, content: str, source_file: str = "") -> str:
        """Add a company document"""
        doc_id = f"{company}_{doc_type}_{hashlib.md5(content[:100].encode()).hexdigest()[:8]}"

        metadata = {
            'company': company,
            'type': doc_type,
            'source_file': source_file,
            'added_at': str(datetime.now())
        }

        return self.vector_store.add_document(doc_id, content, metadata)

    def get_company_promises(self, company: str, query: str = "", limit: int = 5) -> List[Dict]:
        """Get relevant company promises/commitments"""
        search_query = f"{company} {query} promises commitments values ethics sustainability"

        results = self.vector_store.search(
            query=search_query,
            k=limit * 2,  # Get more to filter
            filter_metadata={'company': company}
        )

        # Filter for promise-related content
        promise_keywords = ['commit', 'promise', 'pledge', 'value', 'mission', 'vision', 'responsibility']

        filtered_results = []
        for result in results:
            content_lower = result['content'].lower()
            if any(keyword in content_lower for keyword in promise_keywords):
                filtered_results.append(result)
                if len(filtered_results) >= limit:
                    break

        return filtered_results

    def get_companies(self) -> List[str]:
        """Get list of all companies in the store"""
        companies = set()
        for document in self.vector_store.documents.values():
            company = document.metadata.get('company')
            if company:
                companies.add(company)
        return sorted(list(companies))


# Test function
def test_vector_store():
    """Test the vector store functionality"""
    store = VectorStore()

    # Add test documents
    test_docs = [
        ("apple_esg_1", "Apple is committed to carbon neutrality by 2030 and responsible sourcing",
         {"company": "Apple", "type": "ESG"}),
        ("apple_conduct_1", "Apple maintains high ethical standards in all business dealings",
         {"company": "Apple", "type": "Conduct"}),
        ("google_mission_1", "Google's mission is to organize world's information and make it accessible",
         {"company": "Google", "type": "Mission"})
    ]

    store.add_documents(test_docs)

    # Test search
    results = store.search("carbon environmental sustainability", k=2)
    print(f"Search results: {len(results)}")
    for result in results:
        print(f"- {result['id']}: {result['score']:.3f}")

    # Save index
    store.save_index()

    print("Vector store test completed")

if __name__ == "__main__":
    test_vector_store()