from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.data.sessions import sessions

from src.utils.utils import *

router1 = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory="frontend/templates")

# Роут для страницы регистрации
@router1.get("/auth/register", response_class=HTMLResponse)
def get_register(request: Request):
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request, "error": None}
    )

# Обработка формы регистрации
@router1.post("/auth/register", response_class=HTMLResponse)
def register_user(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    errors = []
    if password != confirm_password:
        errors.append("Пароли не совпадают")
    if len(login) < 6:
        errors.append("Логин должен быть минимум 6 символов")
    if len(password) < 8:
        errors.append("Пароль должен быть минимум 8 символов")
    if get_user_by_login(login):
        errors.append("Пользователь уже существует")

    if errors:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "errors": errors},
            status_code=400
        )

    create_user(login, password)
    session_id = give_session(login, sessions)
    redirect = RedirectResponse(url="/dashboard", status_code=303)
    redirect.set_cookie(
        key="session_id",
        value=str(session_id),
        httponly=True,
        max_age=60 * 60 * 24 * 30,
        secure=False,
        samesite="Lax"
    )
    return redirect


# Роут для страницы логина
@router1.get("/auth/login", response_class=HTMLResponse)
def get_login(request: Request):  # Изменил имя функции с get_register на get_login
    return templates.TemplateResponse(
        "auth/login.html",  # Убедитесь, что файл login.html находится в папке templates/auth
        {"request": request, "error": None}
    )

# Обработка формы логина
@router1.post("/auth/login", response_class=HTMLResponse)
def perform_auth(
    request: Request,
    login: str = Form(...),
    password: str = Form(...)
):
    user = get_user_by_login(login)
    if not user or not verify_password(password, user.hash_password):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Неверный логин или пароль"},
            status_code=401
        )

    session_cookie = request.cookies.get("session_id")
    if session_cookie and session_cookie.isdigit():
        session_id = int(session_cookie)
        if any(s["session_id"] == session_id and s["is_active"] for s in sessions):
            return RedirectResponse(url="/dashboard", status_code=303)

    session_id = give_session(login, sessions)
    redirect = RedirectResponse(url="/dashboard", status_code=303)
    redirect.set_cookie(
        key="session_id",
        value=str(session_id),
        httponly=True,
        max_age=60 * 60 * 24 * 30,
        secure=False,
        samesite="Lax"
    )
    return redirect
