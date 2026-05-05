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
    convs = db.query(Conversation).filter(Conversation.parent_conversation_id == None).all()
    return [{
        "id": c.id,
        "name": c.name,
        "document_id": c.document_id,
        "created_at": c.created_at,
        "message_count": len(c.messages),
        "has_forks": len(c.child_conversations) > 0,
        "fork_count": len(c.child_conversations)
    } for c in convs]

@router.get("/{conv_id}/tree")
async def get_conversation_tree(conv_id: str, db: Session = Depends(get_db)):
    """Get conversation branching tree."""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    def build_tree(c):
        return {
            "id": c.id,
            "name": c.name,
            "is_fork": c.parent_conversation_id is not None,
            "message_count": len(c.messages),
            "children": [build_tree(child) for child in c.child_conversations]
        }

    root = conv
    while root.parent_conversation_id:
        root = db.query(Conversation).filter(Conversation.id == root.parent_conversation_id).first()

    return build_tree(root)

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
    db.flush()

    # Copy messages up to fork point
    all_messages = db.query(Message).filter(Message.conversation_id == conv_id).all()
    fork_point_idx = 0
    for idx, msg in enumerate(all_messages):
        if msg.id == message_id:
            fork_point_idx = idx
            break

    for msg in all_messages[:fork_point_idx + 1]:
        new_msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=fork_id,
            role=msg.role,
            content=msg.content,
            model_used=msg.model_used,
            tools_called=msg.tools_called,
            cited_sources=msg.cited_sources,
        )
        db.add(new_msg)

    db.commit()

    return {
        "id": fork_conv.id,
        "name": fork_conv.name,
        "parent_id": fork_conv.parent_conversation_id,
        "created_at": fork_conv.created_at,
        "message_count": fork_point_idx + 1
    }

@router.post("/{conv_id}/merge")
async def suggest_merge(conv_id: str, db: Session = Depends(get_db)):
    """Get merge suggestions for a fork."""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv or not conv.parent_conversation_id:
        raise HTTPException(status_code=400, detail="Not a fork")

    parent = db.query(Conversation).filter(Conversation.id == conv.parent_conversation_id).first()
    parent_msgs = db.query(Message).filter(Message.conversation_id == parent.id).all()
    fork_msgs = db.query(Message).filter(Message.conversation_id == conv_id).all()

    new_messages = fork_msgs[len(parent_msgs):]

    return {
        "parent_id": parent.id,
        "fork_id": conv_id,
        "new_messages": [
            {"id": m.id, "role": m.role, "content": m.content[:200]}
            for m in new_messages
        ],
        "suggestion": "Consider merging these new messages back to parent" if new_messages else "No new messages"
    }

@router.post("/{conv_id}/merge-confirm")
async def confirm_merge(conv_id: str, db: Session = Depends(get_db)):
    """Merge fork back to parent."""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv or not conv.parent_conversation_id:
        raise HTTPException(status_code=400, detail="Not a fork")

    parent_id = conv.parent_conversation_id
    parent_msgs = db.query(Message).filter(Message.conversation_id == parent_id).count()
    fork_msgs = db.query(Message).filter(Message.conversation_id == conv_id).all()

    for msg in fork_msgs[parent_msgs:]:
        new_msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=parent_id,
            role=msg.role,
            content=msg.content,
            model_used=msg.model_used,
            tools_called=msg.tools_called,
            cited_sources=msg.cited_sources,
        )
        db.add(new_msg)

    conv.is_merged_to_parent = True
    db.commit()

    return {
        "status": "merged",
        "fork_id": conv_id,
        "parent_id": parent_id
    }
