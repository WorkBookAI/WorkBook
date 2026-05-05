from typing import Optional
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

class SuggestNoteTool:
    @staticmethod
    def suggest(
        document_id: str,
        page_number: Optional[int],
        note_content: str,
        db: Session = None,
    ) -> dict:
        """Suggest a note to be added to material."""
        if not db:
            return {"error": "Database not available"}

        from app.db.models import Document, Note

        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return {"error": "Document not found"}

        note_id = str(uuid.uuid4())
        note = Note(
            id=note_id,
            document_id=document_id,
            page_number=page_number,
            content=note_content,
            added_by="model",
        )
        db.add(note)
        db.commit()

        return {
            "status": "note_added",
            "note_id": note_id,
            "content": note_content,
            "document": doc.name,
        }
