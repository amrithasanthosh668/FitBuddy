from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import re

from app.gemini_service import (
    generate_workout_gemini,
    generate_nutrition_tip_with_flash,
    update_workout_plan
)

from app.database import Base, engine, SessionLocal
from app import models


app = FastAPI(title="FitBuddy")

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def clean_text(text):
    text = re.sub(r"###", "", text)
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"\*", "", text)
    text = re.sub(r"---", "", text)
    return text.strip()


def format_plan(plan):

    days = []

    matches = list(
        re.finditer(
            r"(?im)^\s*day\s*(\d+)\s*:?\s*$",
            plan
        )
    )

    for i, match in enumerate(matches):

        day_number = int(match.group(1))

        if day_number < 1 or day_number > 7:
            continue

        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            next_section = re.search(
                r"(?im)^\s*(?:recovery|healthy eating|healthy habits|nutrition)",
                plan[start:]
            )

            if next_section:
                end = start + next_section.start()
            else:
                end = len(plan)

        content = clean_text(
            plan[start:end].strip()
        )

        days.append({
            "day": f"Day {day_number}",
            "content": content
        })

    recovery = ""

    recovery_match = re.search(
        r"(?is)(?:^|\n)\s*(?:recovery|simple recovery tips)\s*:?\s*(.*?)(?=\n\s*(?:healthy eating|healthy habits|nutrition)|$)",
        plan
    )

    if recovery_match:
        recovery = clean_text(
            recovery_match.group(1)
        )

    healthy = ""

    healthy_match = re.search(
        r"(?is)(?:^|\n)\s*(?:healthy eating.*?hydration guidance|healthy habits|nutrition(?: and hydration)? tips?)\s*:?\s*(.*)$",
        plan
    )

    if healthy_match:
        healthy = clean_text(
            healthy_match.group(1)
        )

    return days, recovery, healthy


@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# Document-required route:
# /generate-workout

# Old route is also kept so the existing form continues to work.
@app.post("/generate-workout")
@app.post("/generate")
def generate_plan(
    request: Request,
    name: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    level: str = Form(...),
    intensity: str = Form(...),
    time: str = Form(...)
):

    db = SessionLocal()

    user = models.User(
        name=name,
        user_code=user_id,
        age=age,
        weight=weight,
        goal=goal,
        level=level,
        intensity=intensity,
        available_time=time
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate workout plan using Gemini
    workout_plan = generate_workout_gemini(
        age,
        weight,
        goal,
        level,
        intensity,
        time
    )

    # Generate nutrition tip separately
    nutrition_tip = generate_nutrition_tip_with_flash(
        goal
    )

    # Combine both so the existing result page can display them
    plan = workout_plan + "\n\nNUTRITION\n" + nutrition_tip

    fitness_plan = models.FitnessPlan(
        user_id=user.id,
        plan=plan
    )

    db.add(fitness_plan)
    db.commit()
    db.refresh(fitness_plan)

    db.close()

    days, recovery, healthy = format_plan(plan)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "name": name,
            "user_id": user_id,
            "age": age,
            "weight": weight,
            "goal": goal,
            "level": level,
            "intensity": intensity,
            "time": time,
            "days": days,
            "recovery": recovery,
            "healthy": healthy,
            "plan_id": fitness_plan.id,
            "message": ""
        }
    )


# Document-required route:
# /submit-feedback

# Old route is also kept.
@app.post("/submit-feedback")
@app.post("/feedback")
def feedback_plan(
    request: Request,
    plan_id: int = Form(...),
    feedback: str = Form(...)
):

    db = SessionLocal()

    fitness_plan = db.query(
        models.FitnessPlan
    ).filter(
        models.FitnessPlan.id == plan_id
    ).first()

    if not fitness_plan:

        db.close()

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "name": "",
                "user_id": "",
                "age": "",
                "weight": "",
                "goal": "",
                "level": "",
                "intensity": "",
                "time": "",
                "days": [],
                "recovery": "",
                "healthy": "",
                "plan_id": plan_id,
                "message": ""
            }
        )

    user = db.query(
        models.User
    ).filter(
        models.User.id == fitness_plan.user_id
    ).first()

    # Update plan using user feedback
    updated_plan = update_workout_plan(
        fitness_plan.plan,
        feedback
    )

    fitness_plan.updated_plan = updated_plan
    fitness_plan.feedback = feedback

    db.commit()

    days, recovery, healthy = format_plan(
        updated_plan
    )

    name = user.name
    user_id = user.user_code
    age = user.age
    weight = user.weight
    goal = user.goal
    level = user.level
    intensity = user.intensity
    time = user.available_time

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "name": name,
            "user_id": user_id,
            "age": age,
            "weight": weight,
            "goal": goal,
            "level": level,
            "intensity": intensity,
            "time": time,
            "days": days,
            "recovery": recovery,
            "healthy": healthy,
            "plan_id": plan_id,
            "message": "Your plan has been updated successfully!"
        }
    )


# Document-required route:
# /view-all-users
@app.get("/view-all-users")
def view_all_users(request: Request):

    db = SessionLocal()

    users = db.query(
        models.User
    ).all()

    for user in users:
        user.fitness_plans

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": users
        }
    )


# Keep /admin working as an additional route.
@app.get("/admin")
def admin_view(request: Request):

    db = SessionLocal()

    users = db.query(
        models.User
    ).all()

    for user in users:
        user.fitness_plans

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": users
        }
    )


@app.post("/delete-user")
def delete_user(
    user_id: int = Form(...)
):

    db = SessionLocal()

    user = db.query(
        models.User
    ).filter(
        models.User.id == user_id
    ).first()

    if user:

        db.query(
            models.FitnessPlan
        ).filter(
            models.FitnessPlan.user_id == user.id
        ).delete(
            synchronize_session=False
        )

        db.delete(user)

        db.commit()

    db.close()

    return RedirectResponse(
        url="/view-all-users?deleted=1",
        status_code=303
    )


@app.get("/health")
def health():

    return {
        "status": "FitBuddy is running"
    }