import os
import PyPDF2
from pathlib import Path
from typing import Dict, List
import time
from datetime import datetime

class DocumentProcessor:
    def __init__(self, docs_directory="company_documents"):
        self.docs_directory = docs_directory
        self.processed_docs = {}

    def extract_pdf_content(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            print(f"Error processing PDF {file_path}: {e}")
            return ""

    def extract_text_content(self, file_path: str) -> str:
        """Extract content from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error processing text file {file_path}: {e}")
            return ""

    def process_company_documents(self, company_id: str) -> Dict:
        """Process all documents for a specific company"""
        company_path = Path(self.docs_directory) / company_id

        if not company_path.exists():
            print(f"No documents found for company: {company_id}")
            return {}

        documents = {}

        for file_path in company_path.glob("*"):
            if file_path.is_file():
                file_ext = file_path.suffix.lower()

                if file_ext == '.pdf':
                    content = self.extract_pdf_content(str(file_path))
                elif file_ext in ['.txt', '.md']:
                    content = self.extract_text_content(str(file_path))
                else:
                    continue

                if content:
                    doc_type = file_path.stem
                    documents[doc_type] = {
                        'content': content,
                        'file_path': str(file_path),
                        'timestamp': int(file_path.stat().st_mtime),
                        'document_type': doc_type
                    }

        self.processed_docs[company_id] = documents
        return documents

    def get_company_promises(self, company_id: str, keywords: List[str] = None) -> str:
        """Extract company promises/commitments from documents"""
        if company_id not in self.processed_docs:
            self.process_company_documents(company_id)

        company_docs = self.processed_docs.get(company_id, {})
        promises = []

        # Keywords to look for promises/commitments
        if not keywords:
            keywords = [
                'commitment', 'promise', 'pledge', 'value', 'mission', 'vision',
                'environmental', 'sustainability', 'ethical', 'responsibility',
                'employee', 'diversity', 'inclusion', 'community'
            ]

        for doc_type, doc_data in company_docs.items():
            content = doc_data['content']
            # Simple keyword-based extraction (can be enhanced with NLP)
            sentences = content.split('.')

            for sentence in sentences:
                if any(keyword.lower() in sentence.lower() for keyword in keywords):
                    promises.append(f"[{doc_type}] {sentence.strip()}")

        return "\n".join(promises[:10])  # Return top 10 relevant sentences

    def create_sample_documents(self):
        """Create sample company documents for demo"""
        sample_company = "TechCorp"
        company_dir = Path(self.docs_directory) / sample_company
        company_dir.mkdir(parents=True, exist_ok=True)

        # Create sample ESG report
        esg_content = """
        TechCorp Environmental, Social & Governance Report 2024

        Our Environmental Commitments:
        - TechCorp pledges to achieve carbon neutrality by 2030
        - We are committed to reducing water usage by 50% across all facilities
        - Zero waste to landfill commitment for all manufacturing operations
        - Investment of $1 billion in renewable energy projects

        Our Social Values:
        - TechCorp believes in creating an inclusive workplace for all employees
        - We promise equal pay for equal work across all demographics
        - Commitment to employee wellbeing and work-life balance
        - Supporting local communities through our volunteer programs

        Governance Principles:
        - Transparent reporting of all business practices
        - Ethical treatment of suppliers and partners
        - Regular audits to ensure compliance with all regulations
        """

        with open(company_dir / "esg_report_2024.txt", "w") as f:
            f.write(esg_content)

        # Create sample code of conduct
        conduct_content = """
        TechCorp Code of Conduct

        At TechCorp, we uphold the highest standards of integrity:

        Environmental Responsibility:
        - We commit to minimizing our environmental footprint
        - All operations must comply with environmental regulations
        - Employees are encouraged to adopt sustainable practices

        Employee Treatment:
        - TechCorp values diversity and inclusion in all aspects of work
        - We provide safe, healthy working conditions for all employees
        - No tolerance for discrimination or harassment of any kind
        - Fair compensation and benefits for all team members

        Business Ethics:
        - Honest and transparent business dealings
        - Respect for intellectual property and privacy
        - No conflicts of interest in business relationships
        """

        with open(company_dir / "code_of_conduct.txt", "w") as f:
            f.write(conduct_content)

        print(f"Sample documents created for {sample_company}")

if __name__ == "__main__":
    # Demo usage
    processor = DocumentProcessor()
    processor.create_sample_documents()

    # Process the sample company
    docs = processor.process_company_documents("TechCorp")
    print("Processed documents:", list(docs.keys()))

    # Extract promises
    promises = processor.get_company_promises("TechCorp")
    print("\nCompany Promises:")
    print(promises)