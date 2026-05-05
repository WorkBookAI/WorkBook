from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    file_type = Column(String)  # pdf, docx, pptx, code, image
    path = Column(String, nullable=False)
    size = Column(Integer)
    content_extracted = Column(Text)  # indexed, full text
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    doc_metadata = Column(JSON)  # pages, author, etc

    conversations = relationship("Conversation", back_populates="document")
    notes = relationship("Note", back_populates="document")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, default="Untitled")
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_conversation_id = Column(String, ForeignKey("conversations.id"), nullable=True)
    is_merged_to_parent = Column(Boolean, default=False)

    messages = relationship("Message", back_populates="conversation")
    document = relationship("Document", back_populates="conversations")
    child_conversations = relationship("Conversation", remote_side=[parent_conversation_id])

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String)  # user, assistant
    content = Column(Text, nullable=False)
    model_used = Column(String)
    tokens_used = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    tools_called = Column(JSON)  # list of tool calls
    cited_sources = Column(JSON)  # source citations

    conversation = relationship("Conversation", back_populates="messages")

class Note(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer)
    content = Column(Text, nullable=False)
    added_by = Column(String)  # user, model
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="notes")

class Rule(Base):
    __tablename__ = "rules"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
