from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import pickle, os
import pandas as pd

import database, crud, models, auth

# Config
SECRET_KEY = "your-very-secret-key"
MODEL_FILE = 'rf_cgpa_model.pkl'
SCALER_FILE = 'scaler.pkl'

# App init
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load ML artifacts
if not os.path.exists(MODEL_FILE) or not os.path.exists(SCALER_FILE):
    raise RuntimeError("Model or scaler pickle missing.")
with open(MODEL_FILE,'rb') as f: model = pickle.load(f)
with open(SCALER_FILE,'rb') as f: scaler = pickle.load(f)

# Home -> redirect to login
@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse("/user/login")

# -------- User routes --------
@app.get("/user/signup", response_class=HTMLResponse)
async def user_signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request":request})

# -------- User routes --------
@app.get("/user/signup", response_class=HTMLResponse)
async def user_signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request":request})

@app.post("/user/signup")
async def user_signup(request: Request,
    email: str = Form(...), name: str = Form(...), password: str = Form(...)):
    exists = crud.get_user_by_email(email)
    if exists:
        return templates.TemplateResponse("signup.html", {"request":request, "error":"Email already registered."})
    crud.create_user(email, name, password)
    return RedirectResponse("/user/login", status_code=302)

@app.get("/user/login", response_class=HTMLResponse)
async def user_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request":request, "role":"user"})

@app.post("/user/login")
async def user_login(request: Request,
    email: str = Form(...), password: str = Form(...)):
    user = crud.authenticate_user(email, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request":request, "error":"Invalid credentials.", "role":"user"})
    request.session.update({"user_id":user.id, "email":user.email, "is_admin":False})
    return RedirectResponse("/user/dashboard", status_code=302)

@app.post("/user/logout")
async def user_logout(request: Request):
    request.session.clear()  # Clear the session
    return RedirectResponse("/user/login", status_code=302)

@app.get("/user/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request, current=Depends(auth.get_current_user)):
    preds = crud.get_predictions(current.id)
    if not preds:
        return RedirectResponse("/user/predict", status_code=302)
    last = preds[-1]
    return templates.TemplateResponse("dashboard.html", {"request":request, "pred":last})

@app.get("/user/predict", response_class=HTMLResponse)
async def predict_form(request: Request, current=Depends(auth.get_current_user)):
    return templates.TemplateResponse("predict.html", {"request":request})

@app.post("/user/predict", response_class=HTMLResponse)
async def predict_submit(request: Request,
    current=Depends(auth.get_current_user),
    Age: int = Form(...), Gender: str = Form(...), HoursOfStudyPerDay: float = Form(...),
    SchoolAttendanceRate: float = Form(...), TuitionAccess: str = Form(...),
    AveragePreviousScores: float = Form(...), ParticipatesInClubs: str = Form(...),
    HoursOfSleep: float = Form(...), BreakfastDaily: str = Form(...),
    ScreenTimeHours: float = Form(...), PhysicalActivityHours: float = Form(...),
    PlaysSport: str = Form(...), MentalHealthScore: int = Form(...),
    StudyEnvironmentRating: int = Form(...), FriendSupportScore: int = Form(...),
    ParentalEducationLevel: str = Form(...), HouseholdIncomeLevel: str = Form(...),
    PartTimeWork: str = Form(...)
):
    gen = {"Female":[1,0,0],"Male":[0,1,0],"Other":[0,0,1]}[Gender]
    yn = lambda v:1 if v=="Yes" else 0
    pedigree={"High school":0,"Graduate":1,"Postgrad":2}
    income={"Low":0,"Medium":1,"High":2}
    payload={
      "Age":Age,
      "Gender_Female":gen[0],"Gender_Male":gen[1],"Gender_Other":gen[2],
      "HoursOfStudyPerDay":HoursOfStudyPerDay,
      "SchoolAttendanceRate":SchoolAttendanceRate,
      "TuitionAccess":yn(TuitionAccess),
      "AveragePreviousScores":AveragePreviousScores,
      "ParticipatesInClubs":yn(ParticipatesInClubs),
      "HoursOfSleep":HoursOfSleep,
      "BreakfastDaily":yn(BreakfastDaily),
      "ScreenTimeHours":ScreenTimeHours,
      "PhysicalActivityHours":PhysicalActivityHours,
      "PlaysSport":yn(PlaysSport),
      "MentalHealthScore":MentalHealthScore,
      "StudyEnvironmentRating":StudyEnvironmentRating,
      "FriendSupportScore":FriendSupportScore,
      "ParentalEducationLevel_Encoded":pedigree[ParentalEducationLevel],
      "HouseholdIncomeLevel_Encoded":income[HouseholdIncomeLevel],
      "PartTimeWork":yn(PartTimeWork)
    }
    if sum([HoursOfStudyPerDay,HoursOfSleep,ScreenTimeHours,PhysicalActivityHours])>24:
        return templates.TemplateResponse("predict.html", {"request":request, "error":"Total hours exceed 24."})
    df = pd.DataFrame([payload])[scaler.feature_names_in_]
    X = scaler.transform(df)
    pred = model.predict(X)[0]
    acc = getattr(model, 'accuracy_', 0.0)
    algo = model.__class__.__name__
    crud.save_prediction(current.id, float(pred), float(acc), algo, payload)
    return RedirectResponse("/user/dashboard", status_code=302)

@app.post("/user/delete")
async def user_delete(request: Request, pred_id: int = Form(...), current=Depends(auth.get_current_user)):
    crud.delete_prediction(pred_id, current.id)
    return RedirectResponse("/user/predict", status_code=302)

# -------- Admin routes --------
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request":request, "role":"admin"})

@app.post("/admin/login")
async def admin_login(request: Request,
    email: str = Form(...), password: str = Form(...)):
    if email!="admin@gmail.com" or password!="Admin@149":
        return templates.TemplateResponse("login.html", {"request":request, "error":"Invalid.", "role":"admin"})
    request.session.update({"is_admin":True})
    return RedirectResponse("/admin/dashboard", status_code=302)
@app.post("/admin/logout")
async def admin_logout(request: Request):
    request.session.clear()  # Clear the session
    return RedirectResponse("/admin/login", status_code=302)

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin=Depends(auth.get_current_admin)):
    users = crud.list_users()
    users_with_last = []
    for u in users:
        preds = crud.get_predictions(u.id)
        last = preds[-1] if preds else None
        users_with_last.append({
            "id":         u.id,
            "name":       u.name,
            "email":      u.email,
            "last_pred":  last.predicted if last else None,
            "last_date":  last.timestamp.split(" ")[0] if last else None
        })
    return templates.TemplateResponse("admin_dashboard.html", {
        "request":     request,
        "users":       users_with_last,
        "total_users": len(users_with_last),
        "crud" : crud
    })


@app.post("/admin/user/delete")
async def admin_delete_user(request: Request, user_id: int = Form(...), admin=Depends(auth.get_current_admin)):
    crud.delete_user(user_id)
    return RedirectResponse("/admin/dashboard", status_code=302)

@app.post("/admin/user/update")
async def admin_update_user(request: Request,
    user_id: int = Form(...), name: str = Form(...), email: str = Form(...), admin=Depends(auth.get_current_admin)):
    crud.update_user(user_id, name, email)
    return RedirectResponse("/admin/dashboard", status_code=302)





if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=True)
