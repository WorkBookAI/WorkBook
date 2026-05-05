from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.db.models import Conversation, Message, Document
from app.core.llm import LLMManager
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

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
    """Add message and get LLM response."""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Store user message
    user_msg_id = str(uuid.uuid4())
    user_msg = Message(
        id=user_msg_id,
        conversation_id=conv_id,
        role="user",
        content=msg.content,
        model_used=msg.model
    )
    db.add(user_msg)
    db.commit()

    # Prepare context
    context = ""
    if conv.document_id:
        doc = db.query(Document).filter(Document.id == conv.document_id).first()
        if doc and doc.content_extracted:
            context = f"Document context:\n{doc.content_extracted[:2000]}\n\n"

    # Build messages for LLM
    messages = [
        {
            "role": m.role,
            "content": m.content
        }
        for m in db.query(Message).filter(Message.conversation_id == conv_id).all()
    ]

    # Get LLM response
    try:
        # Parse provider and model
        provider_model = msg.model.split(":") if ":" in msg.model else [msg.model.split("-")[0], msg.model]
        provider = provider_model[0] if len(provider_model) > 1 else "openai"
        model = msg.model

        llm = LLMManager.get_provider(provider, model)
        response_text = await llm.chat(messages, system_prompt=context)

        # Store assistant response
        asst_msg_id = str(uuid.uuid4())
        asst_msg = Message(
            id=asst_msg_id,
            conversation_id=conv_id,
            role="assistant",
            content=response_text,
            model_used=msg.model
        )
        db.add(asst_msg)
        db.commit()

        return {
            "user_message": {
                "id": user_msg_id,
                "role": "user",
                "content": msg.content,
            },
            "assistant_message": {
                "id": asst_msg_id,
                "role": "assistant",
                "content": response_text,
            }
        }
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
