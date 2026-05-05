from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Document
from app.core.document_processor import DocumentProcessor
from app.core.search import FullTextSearch
import uuid
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path.home() / ".workbook" / "documents"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process document."""
    doc_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    file_type = file.filename.split(".")[-1].lower()

    # Process document
    try:
        extracted = DocumentProcessor.process_document(str(file_path))
        content_text = extracted.get("full_text", "")
    except Exception as e:
        content_text = ""

    doc = Document(
        id=doc_id,
        name=file.filename,
        file_type=file_type,
        path=str(file_path),
        size=len(contents),
        content_extracted=content_text[:50000],  # Store first 50k chars
        metadata={"original_name": file.filename, "processed": True}
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "id": doc.id,
        "name": doc.name,
        "file_type": doc.file_type,
        "size": doc.size,
        "created_at": doc.created_at
    }

@router.get("/")
async def list_documents(db: Session = Depends(get_db)):
    """List all documents."""
    docs = db.query(Document).all()
    return [{
        "id": doc.id,
        "name": doc.name,
        "file_type": doc.file_type,
        "size": doc.size,
        "created_at": doc.created_at
    } for doc in docs]

@router.get("/{doc_id}")
async def get_document(doc_id: str, db: Session = Depends(get_db)):
    """Get document details."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": doc.id,
        "name": doc.name,
        "file_type": doc.file_type,
        "size": doc.size,
        "created_at": doc.created_at,
        "content_extracted": doc.content_extracted[:1000] if doc.content_extracted else None
    }

@router.delete("/{doc_id}")
async def delete_document(doc_id: str, db: Session = Depends(get_db)):
    """Delete document."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    Path(doc.path).unlink(missing_ok=True)
    db.delete(doc)
    db.commit()

    return {"status": "deleted"}

@router.get("/{doc_id}/search")
async def search_document(doc_id: str, q: str = Query(...), db: Session = Depends(get_db)):
    """Search within document content."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not doc.content_extracted:
        raise HTTPException(status_code=400, detail="Document not yet processed")

    results = FullTextSearch.search(q, doc.content_extracted)

    return {
        "query": q,
        "document_id": doc_id,
        "results": results
    }
