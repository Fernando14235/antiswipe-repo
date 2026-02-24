# 🚫 AntiSwipe

Break the "see it → swipe it → forget it" cycle.

A PWA that forces you to hold 3 seconds to mark a task as done.

## Stack
- Frontend: React + Vite + PWA → Vercel
- Backend: FastAPI + SQLAlchemy + JWT + Web Push → Railway

## Run locally

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install && npm run dev
```

## Deploy
- Backend → railway.app
- Frontend → vercel.com
