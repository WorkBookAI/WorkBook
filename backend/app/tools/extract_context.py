from typing import List, Optional
from app.core.search import FullTextSearch
from sqlalchemy.orm import Session

class ExtractContextTool:
    @staticmethod
    def extract(
        query: str,
        document_id: Optional[str],
        max_tokens: int = 1000,
        db: Session = None,
    ) -> dict:
        """Extract relevant context from documents."""
        if not db or not document_id:
            return {"error": "No document context available"}

        from app.db.models import Document
        doc = db.query(Document).filter(Document.id == document_id).first()

        if not doc or not doc.content_extracted:
            return {"error": "Document not found or not processed"}

        results = FullTextSearch.search(query, doc.content_extracted, max_results=5)

        return {
            "query": query,
            "document": {
                "id": doc.id,
                "name": doc.name,
            },
            "results": results,
            "full_text": "\n".join([r["text"] for r in results])
        }
