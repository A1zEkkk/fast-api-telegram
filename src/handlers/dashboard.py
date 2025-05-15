import calendar
from datetime import datetime
from typing import List

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from src.data.sessions import sessions
from src.utils.utils import add_reminderdb, get_reminderdb

router2 = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")


@router2.get("/dashboard/")
@router2.get("/dashboard/{year}/{month}")
def get_dashboard(request: Request, year: int = None, month: int = None):
    session_id = request.cookies.get("session_id")

    if session_id is None or not any(int(session_id) == session["session_id"] for session in sessions):
        return RedirectResponse(url="/auth/login", status_code=302)

    if year is None or month is None:
        today = datetime.today()
        year = today.year
        month = today.month

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1

    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    calendar_data = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    return templates.TemplateResponse("dashboard/calendar.html", {
        "request": request,
        "year": year,
        "month": month_name,
        "weeks": calendar_data,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year
    })


@router2.get("/dashboard/{year}/{month}/{day}")
def get_reminder(year: int, month: str, day: int, request: Request):
    session_id = request.cookies.get("session_id")
    session = next(
        (s for s in sessions if s["session_id"] == int(session_id)) if session_id and session_id.isdigit() else None,
        None)

    if session is None:
        return RedirectResponse(url="/auth/login", status_code=302)

    user = session["user"]

    # Преобразуем строковый или числовой месяц в число
    try:
        if month.isdigit():
            month_number = int(month)
        else:
            month_number = list(calendar.month_name).index(month.capitalize())
        if not 1 <= month_number <= 12:
            raise ValueError
    except ValueError:
        return RedirectResponse(url="/dashboard", status_code=302)

    reminder = get_reminderdb(year, month_number, day, user)
    month = calendar.month_name[month_number].lower()

    return templates.TemplateResponse("dashboard/day.html", {
        "request": request,
        "year": year,
        "month": month,
        "day": day,
        "reminder": reminder
    })


@router2.get("/dashboard/{year}/{month}/{day}/add_reminder")
def show_add_form(year: int, month: str, day: int, request: Request):
    session_id = request.cookies.get("session_id")
    session = next(
        (s for s in sessions if s["session_id"] == int(session_id)) if session_id and session_id.isdigit() else None,
        None
    )

    if session is None:
        return RedirectResponse(url="/auth/login", status_code=302)

    return templates.TemplateResponse("dashboard/add_reminder.html", {
        "request": request,
        "year": year,
        "month": month,
        "day": day
    })



@router2.post("/dashboard/{year}/{month}/{day}/add_reminder")
def add_reminder(year: int, month: str, day: int, reminder: List[str] = Form(...), request: Request = ...):
    try:
        if isinstance(month, int):
            if not (1 <= month <= 12):
                raise ValueError("Invalid month number")
        else:
            month = str(month).capitalize()
            month = list(calendar.month_name).index(month)
            if month == 0:
                raise ValueError("Invalid month name")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid month name or number")

    session_id = request.cookies.get("session_id")
    session = next(
        (s for s in sessions if s["session_id"] == int(session_id)) if session_id and session_id.isdigit() else None,
        None)

    if session is None:
        return RedirectResponse(url="/auth/login", status_code=302)

    user = session["user"]

    # Сохраняем напоминание
    add_reminderdb(year, month, day, reminder, user)

    return RedirectResponse(url=f"/dashboard/{year}/{month}/{day}", status_code=303)
