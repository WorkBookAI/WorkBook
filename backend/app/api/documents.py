from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Document
from app.core.document_processor import DocumentProcessor
from app.core.search import FullTextSearch
import uuid
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

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
        doc_metadata={"original_name": file.filename, "processed": True}
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
    """Get document details with structured content."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    content = {"type": doc.file_type, "content": [], "full_text": ""}

    try:
        logger.info(f"[GET] Processing document: {doc.path}")
        extracted = DocumentProcessor.process_document(doc.path)
        logger.info(f"[GET] Extracted type: {extracted.get('type')}")
        logger.info(f"[GET] Extracted content length: {len(extracted.get('content', []))}")
        logger.info(f"[GET] Extracted full_text length: {len(extracted.get('full_text', ''))}")

        if extracted:
            content = {
                "type": extracted.get("type"),
                "content": extracted.get("content", []),
                "full_text": extracted.get("full_text", "")
            }
            logger.info(f"[GET] Content prepared: type={content['type']}, text_len={len(content['full_text'])}")
    except Exception as e:
        logger.error(f"[GET] Error extracting document {doc_id}: {e}", exc_info=True)

    logger.info(f"[GET] Returning content with full_text length: {len(content.get('full_text', ''))}")
    return {
        "id": doc.id,
        "name": doc.name,
        "file_type": doc.file_type,
        "size": doc.size,
        "created_at": doc.created_at,
        "content": content,
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

@router.get("/{doc_id}/file")
async def get_document_file(doc_id: str, db: Session = Depends(get_db)):
    """Get the raw document file for rendering."""
    from fastapi.responses import FileResponse
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return FileResponse(doc.path, media_type="application/octet-stream", filename=doc.name)

@router.get("/{doc_id}/pdf")
async def get_document_pdf(doc_id: str, db: Session = Depends(get_db)):
    """Convert PPTX to PDF and serve it."""
    from fastapi.responses import FileResponse
    import os

    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        logger.error(f"Document not found: {doc_id}")
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.file_type != 'pptx':
        logger.warning(f"Non-PPTX file requested: {doc.file_type}")
        raise HTTPException(status_code=400, detail="Only PPTX files can be converted to PDF")

    try:
        from app.core.document_processor import DocumentProcessor
        logger.info(f"[PDF] Converting PPTX to PDF: {doc.path}")
        logger.info(f"[PDF] File exists: {os.path.exists(doc.path)}")

        pdf_path = DocumentProcessor.convert_pptx_to_pdf(doc.path)
        logger.info(f"[PDF] PDF path returned: {pdf_path}")
        logger.info(f"[PDF] PDF file exists: {os.path.exists(pdf_path)}")
        logger.info(f"[PDF] PDF file size: {os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0}")

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=doc.name.replace('.pptx', '.pdf')
        )
    except Exception as e:
        logger.error(f"[PDF] Error converting PPTX to PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to convert PPTX: {str(e)}")

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
