from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.db.models import Rule
import uuid

router = APIRouter()

class RuleCreate(BaseModel):
    name: str
    content: str
    active: bool = True

class RuleUpdate(BaseModel):
    name: str = None
    content: str = None
    active: bool = None

@router.get("/")
async def list_rules(db: Session = Depends(get_db)):
    """List all rules."""
    rules = db.query(Rule).all()
    return [{
        "id": r.id,
        "name": r.name,
        "content": r.content,
        "active": r.active,
        "created_at": r.created_at,
    } for r in rules]

@router.post("/")
async def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    """Create a new rule."""
    rule_id = str(uuid.uuid4())
    new_rule = Rule(
        id=rule_id,
        name=rule.name,
        content=rule.content,
        active=rule.active,
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    return {
        "id": new_rule.id,
        "name": new_rule.name,
        "content": new_rule.content,
        "active": new_rule.active,
    }

@router.put("/{rule_id}")
async def update_rule(rule_id: str, rule: RuleUpdate, db: Session = Depends(get_db)):
    """Update a rule."""
    existing = db.query(Rule).filter(Rule.id == rule_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Rule not found")

    if rule.name:
        existing.name = rule.name
    if rule.content:
        existing.content = rule.content
    if rule.active is not None:
        existing.active = rule.active

    db.commit()
    db.refresh(existing)

    return {
        "id": existing.id,
        "name": existing.name,
        "content": existing.content,
        "active": existing.active,
    }

@router.delete("/{rule_id}")
async def delete_rule(rule_id: str, db: Session = Depends(get_db)):
    """Delete a rule."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    db.delete(rule)
    db.commit()

    return {"status": "deleted"}

@router.get("/export/memory")
async def export_as_memory(db: Session = Depends(get_db)):
    """Export rules as MEMORY.md format."""
    rules = db.query(Rule).filter(Rule.active == True).all()

    memory_content = "# Rules\n\n"
    for rule in rules:
        memory_content += f"## {rule.name}\n\n{rule.content}\n\n"

    return {"format": "memory.md", "content": memory_content}
