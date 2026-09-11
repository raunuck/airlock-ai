from fastapi import APIRouter, HTTPException, UploadFile, File, Header
from app.db import list_sessions, create_session, get_session_messages, delete_session
import shutil, uuid, os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/sessions")
def get_sessions(user_id: str | None = Header(None)):
    if not user_id:
        return []
    return list_sessions(user_id)

@router.post("/sessions")
def new_session(user_id: str | None = Header(None)):
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID header missing")
    session_id = create_session(user_id)
    return {"id": session_id, "title": "New chat"}

@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: str, user_id: str | None = Header(None)):
    if not user_id:
        return []
    return get_session_messages(session_id, user_id)

@router.delete("/sessions/{session_id}")
def remove_session(session_id: str, user_id: str | None = Header(None)):
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID header missing")
    delete_session(session_id, user_id)
    return {"deleted": session_id}

@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1]
    stored_name = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_DIR, stored_name)
    try:
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")
    return {"path": path, "filename": file.filename}