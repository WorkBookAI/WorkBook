from typing import Optional, List
from sqlalchemy.orm import Session

class SummarizeTool:
    @staticmethod
    def summarize(
        document_id: str,
        include_chat_context: bool = True,
        db: Session = None,
    ) -> dict:
        """Summarize material with optional chat context."""
        if not db:
            return {"error": "Database not available"}

        from app.db.models import Document, Conversation, Message

        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc or not doc.content_extracted:
            return {"error": "Document not found or not processed"}

        summary = {
            "document": {
                "id": doc.id,
                "name": doc.name,
                "type": doc.file_type,
            },
            "material_summary": f"Summary of {doc.name} (first 500 chars of content):\n{doc.content_extracted[:500]}...",
            "chat_context": [],
        }

        if include_chat_context:
            # Find conversations related to this document
            convs = db.query(Conversation).filter(Conversation.document_id == document_id).all()
            for conv in convs:
                messages = db.query(Message).filter(Message.conversation_id == conv.id).limit(5).all()
                summary["chat_context"].extend([
                    {"role": m.role, "content": m.content[:200]}
                    for m in messages
                ])

        return summary
