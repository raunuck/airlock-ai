from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from app.db import create_user, verify_user

router = APIRouter(prefix="/auth", tags=["auth"])

class UserAuthRequest(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(req: UserAuthRequest):
    try:
        user_id = create_user(req.username, req.password)
        return {"status": "success", "user_id": user_id, "username": req.username}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(req: UserAuthRequest, response: Response):
    user = verify_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # For a simple local session header approach, you can return the user_id directly
    # or set a secure cookie. Returning user_id allows the frontend to store it in localStorage.
    return {
        "status": "success",
        "user_id": user["id"],
        "username": user["username"]
    }