from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Task, PushSubscription
from app.routers.push import send_push

scheduler = BackgroundScheduler()

def check_reminders():
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=2)
        tasks = db.query(Task).filter(
            Task.is_done == False,
            Task.notified == False,
            Task.remind_at != None,
            Task.remind_at <= now,
            Task.remind_at >= window_start,
        ).all()
        for task in tasks:
            subs = db.query(PushSubscription).filter(PushSubscription.user_id == task.user_id).all()
            for sub in subs:
                send_push(sub, title=f"⏰ {task.title}", body="Hold 3 seconds to mark it done — don't just swipe!", url="/")
            task.notified = True
            db.commit()
    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(check_reminders, "interval", minutes=1)
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()
