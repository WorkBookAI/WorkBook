from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.db.models import Conversation, Message, Document
import uuid
from datetime import datetime

router = APIRouter()

class MessageCreate(BaseModel):
    content: str
    model: str = "gpt-3.5-turbo"

class ConversationCreate(BaseModel):
    name: str = "Untitled"
    document_id: str = None

@router.post("/")
async def create_conversation(conv: ConversationCreate, db: Session = Depends(get_db)):
    """Create new conversation."""
    if conv.document_id:
        doc = db.query(Document).filter(Document.id == conv.document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

    conv_id = str(uuid.uuid4())
    new_conv = Conversation(
        id=conv_id,
        name=conv.name,
        document_id=conv.document_id
    )
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)

    return {
        "id": new_conv.id,
        "name": new_conv.name,
        "document_id": new_conv.document_id,
        "created_at": new_conv.created_at
    }

@router.get("/")
async def list_conversations(db: Session = Depends(get_db)):
    """List all conversations."""
    convs = db.query(Conversation).all()
    return [{
        "id": c.id,
        "name": c.name,
        "document_id": c.document_id,
        "created_at": c.created_at,
        "message_count": len(c.messages)
    } for c in convs]

@router.get("/{conv_id}")
async def get_conversation(conv_id: str, db: Session = Depends(get_db)):
    """Get conversation with messages."""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "id": conv.id,
        "name": conv.name,
        "document_id": conv.document_id,
        "created_at": conv.created_at,
        "messages": [{
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at
        } for msg in conv.messages]
    }

@router.post("/{conv_id}/messages")
async def add_message(conv_id: str, msg: MessageCreate, db: Session = Depends(get_db)):
    """Add message to conversation (stores user message only)."""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_id = str(uuid.uuid4())
    new_msg = Message(
        id=msg_id,
        conversation_id=conv_id,
        role="user",
        content=msg.content,
        model_used=msg.model
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)

    return {
        "id": new_msg.id,
        "role": new_msg.role,
        "content": new_msg.content,
        "created_at": new_msg.created_at
    }

@router.post("/{conv_id}/fork")
async def fork_conversation(conv_id: str, message_id: str, db: Session = Depends(get_db)):
    """Fork conversation at specific message."""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    fork_id = str(uuid.uuid4())
    fork_conv = Conversation(
        id=fork_id,
        name=f"{conv.name} (fork)",
        document_id=conv.document_id,
        parent_conversation_id=conv_id
    )
    db.add(fork_conv)
    db.commit()

    return {
        "id": fork_conv.id,
        "name": fork_conv.name,
        "parent_id": fork_conv.parent_conversation_id,
        "created_at": fork_conv.created_at
    }
