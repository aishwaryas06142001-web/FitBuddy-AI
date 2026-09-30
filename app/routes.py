from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import ValidationError

from .database import get_db, save_user, save_plan, get_user, get_latest_plan, update_plan, get_all_users, delete_user
from .schemas import UserInput, FeedbackRequest
from .ai import ai_service

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def render_error(request: Request, message: str, status_code: int = 400):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"error": message},
        status_code=status_code,
    )

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    name: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(name=name, user_id=user_id, age=age, weight=weight, goal=goal, intensity=intensity)
    except ValidationError as exc:
        return render_error(request, exc.errors()[0]["msg"])

    try:
        user = save_user(db, data.model_dump())
        workout = ai_service.generate_workout(user)
        tip = ai_service.generate_nutrition_tip(user.goal)
        plan = save_plan(db, user, workout, tip)
    except Exception as exc:
        return render_error(request, f"AI generation failed: {exc}", 502)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={"user": user, "plan": plan, "message": None},
    )

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = FeedbackRequest(user_id=user_id, feedback=feedback)
    except ValidationError as exc:
        return render_error(request, exc.errors()[0]["msg"])

    user = get_user(db, data.user_id)
    if not user:
        return render_error(request, "User ID was not found.", 404)
    plan = get_latest_plan(db, user)
    if not plan:
        return render_error(request, "No workout plan exists for this user.", 404)

    try:
        revised = ai_service.update_workout(user, plan.updated_plan or plan.original_plan, data.feedback)
        update_plan(db, plan, revised, data.feedback)
    except Exception as exc:
        return render_error(request, f"Plan update failed: {exc}", 502)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={"user": user, "plan": plan, "message": "Your workout plan has been updated."},
    )

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = get_all_users(db)
    rows = [{"user": user, "plan": get_latest_plan(db, user)} for user in users]
    return templates.TemplateResponse(request=request, name="all_users.html", context={"rows": rows})

@router.post("/delete-user")
def remove_user(user_id: str = Form(...), db: Session = Depends(get_db)):
    delete_user(db, user_id)
    return RedirectResponse("/view-all-users", status_code=status.HTTP_303_SEE_OTHER)
