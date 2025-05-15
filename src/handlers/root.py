from fastapi import APIRouter, Request

from fastapi.responses import RedirectResponse

from src.data.sessions import sessions


router3 = APIRouter()

@router3.get("/")
def root(request: Request):
    session_id = request.cookies.get("session_id")

    if session_id is None or not any(int(session_id) == session["session_id"] for session in sessions):
        return RedirectResponse(url="/auth/login", status_code=302)

    return RedirectResponse(url="/dashboard")