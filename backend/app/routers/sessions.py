from fastapi import APIRouter, HTTPException, UploadFile, File, Header, Request
from app.db import list_sessions, create_session, get_session_messages, delete_session, get_connection
import shutil, uuid, os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def resolve_user_id(request: Request, user_id: str | None = None) -> str | None:
    candidate = user_id or request.headers.get("user-id") or request.headers.get("user_id") or request.headers.get("User-Id")
    if candidate and candidate.strip() and candidate not in ("undefined", "null", "None"):
        return candidate.strip()
    conn = get_connection()
    default_user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
    conn.close()
    return default_user["id"] if default_user else None

@router.get("/sessions")
def get_sessions(request: Request, user_id: str | None = Header(None)):
    uid = resolve_user_id(request, user_id)
    if not uid:
        return []
    return list_sessions(uid)

@router.post("/sessions")
def new_session(request: Request, user_id: str | None = Header(None)):
    uid = resolve_user_id(request, user_id)
    if not uid:
        raise HTTPException(status_code=400, detail="User ID header missing")
    session_id = create_session(uid)
    return {"id": session_id, "title": "New chat"}

@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: str, request: Request, user_id: str | None = Header(None)):
    uid = resolve_user_id(request, user_id)
    if not uid:
        return []
    return get_session_messages(session_id, uid)

@router.delete("/sessions/{session_id}")
def remove_session(session_id: str, request: Request, user_id: str | None = Header(None)):
    uid = resolve_user_id(request, user_id)
    if not uid:
        raise HTTPException(status_code=400, detail="User ID header missing")
    delete_session(session_id, uid)
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