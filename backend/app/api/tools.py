from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.tools.extract_context import ExtractContextTool
from app.tools.suggest_note import SuggestNoteTool
from app.tools.search_web import SearchWebTool
from app.tools.summarize import SummarizeTool
from app.tools.answer_from_source import AnswerFromSourceTool

router = APIRouter()

class ExtractContextRequest(BaseModel):
    query: str
    document_id: str
    max_tokens: int = 1000

class SuggestNoteRequest(BaseModel):
    document_id: str
    page_number: int = None
    note_content: str

class SummarizeRequest(BaseModel):
    document_id: str
    include_chat_context: bool = True

class AnswerFromSourceRequest(BaseModel):
    question: str
    document_id: str = None

@router.post("/extract-context")
async def extract_context(req: ExtractContextRequest, db: Session = Depends(get_db)):
    """Extract relevant context from document."""
    result = ExtractContextTool.extract(req.query, req.document_id, req.max_tokens, db)
    return result

@router.post("/suggest-note")
async def suggest_note(req: SuggestNoteRequest, db: Session = Depends(get_db)):
    """Suggest a note to add to material."""
    result = SuggestNoteTool.suggest(req.document_id, req.page_number, req.note_content, db)
    return result

@router.post("/search-web")
async def search_web(query: str):
    """Search the web."""
    result = await SearchWebTool.search(query)
    return result

@router.post("/summarize")
async def summarize(req: SummarizeRequest, db: Session = Depends(get_db)):
    """Summarize material."""
    result = SummarizeTool.summarize(req.document_id, req.include_chat_context, db)
    return result

@router.post("/answer-from-source")
async def answer_from_source(req: AnswerFromSourceRequest, db: Session = Depends(get_db)):
    """Answer question from document source."""
    result = AnswerFromSourceTool.answer(req.question, req.document_id, db)
    return result
