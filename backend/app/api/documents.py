from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Document
import uuid
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path.home() / ".workbook" / "documents"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and store document."""
    doc_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    doc = Document(
        id=doc_id,
        name=file.filename,
        file_type=file.filename.split(".")[-1].lower(),
        path=str(file_path),
        size=len(contents),
        metadata={"original_name": file.filename}
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
