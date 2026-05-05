from typing import Optional
from app.core.search import FullTextSearch
from sqlalchemy.orm import Session

class AnswerFromSourceTool:
    @staticmethod
    def answer(
        question: str,
        document_id: Optional[str],
        db: Session = None,
    ) -> dict:
        """Answer question directly from document source."""
        if not db or not document_id:
            return {"error": "No document source available"}

        from app.db.models import Document

        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc or not doc.content_extracted:
            return {"error": "Document not found or not processed"}

        # Search for relevant content
        sources = FullTextSearch.search(question, doc.content_extracted, max_results=3)

        return {
            "question": question,
            "document": {
                "id": doc.id,
                "name": doc.name,
            },
            "answer": " ".join([s["text"] for s in sources]),
            "sources": [
                {
                    "line": s["line"],
                    "text": s["text"],
                    "score": s["score"],
                }
                for s in sources
            ],
            "has_sources": len(sources) > 0,
        }
