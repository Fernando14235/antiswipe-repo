from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import Task, User
from app.schemas import TaskCreate, TaskUpdate, TaskOut
from app.auth import get_current_user

router = APIRouter()

@router.get("/stats/summary")
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = db.query(Task).filter(Task.user_id == current_user.id).count()
    done = db.query(Task).filter(Task.user_id == current_user.id, Task.is_done == True).count()
    total_swipes = db.query(func.sum(Task.swiped_count)).filter(Task.user_id == current_user.id).scalar() or 0
    return {"total_tasks": total, "completed": done, "pending": total - done, "total_swipes_avoided": total_swipes}

@router.get("/", response_model=List[TaskOut])
def get_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Task).filter(Task.user_id == current_user.id).order_by(Task.created_at.desc()).all()

@router.post("/", response_model=TaskOut)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = Task(**task.dict(), user_id=current_user.id)
    db.add(db_task); db.commit(); db.refresh(db_task)
    return db_task

@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(task, field, value)
    if data.remind_at is not None:
        task.notified = False
    db.commit(); db.refresh(task)
    return task

@router.patch("/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_done = True
    task.completed_at = datetime.utcnow()
    db.commit(); db.refresh(task)
    return task

@router.patch("/{task_id}/swipe", response_model=TaskOut)
def register_swipe(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.swiped_count += 1
    db.commit(); db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task); db.commit()
    return {"ok": True}
