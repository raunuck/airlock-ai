from fastapi import APIRouter, HTTPException, UploadFile, File
from app.db import list_sessions, create_session, get_session_messages, delete_session
import shutil, uuid, os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/sessions")
def get_sessions():
    return list_sessions()

@router.post("/sessions")
def new_session():
    session_id = create_session()
    return {"id": session_id, "title": "New chat"}

@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: str):
    return get_session_messages(session_id)

@router.delete("/sessions/{session_id}")
def remove_session(session_id: str):
    delete_session(session_id)
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