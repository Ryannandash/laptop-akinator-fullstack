import os
import re
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from . import database as db
from . import auth
from . import engine
from .data import SYMPTOMS, DAMAGES

app = FastAPI(title="Laptop Akinator API", version="1.0.0")

origins_env = os.environ.get("FRONTEND_ORIGIN", "*")
origins = [o.strip() for o in origins_env.split(",")] if origins_env != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()


# ---------------------------------------------------------------- schemas --
class RegisterBody(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class StartBody(BaseModel):
    user_id: str | None = None


class AnswerBody(BaseModel):
    symptom_id: str
    answer_value: str  # yes | probably_yes | dont_know | probably_not | no


class ProcessBody(BaseModel):
    consultation_id: str | None = None
    symptom_ids: dict[str, str]  # {symptom_id: answer_value}


class FeedbackBody(BaseModel):
    is_correct: bool
    actual_damage_id: str | None = None


VALID_ANSWERS = {"yes", "probably_yes", "dont_know", "probably_not", "no"}


# --------------------------------------------------------------- A. AUTH --
@app.post("/api/auth/register")
def register(body: RegisterBody):
    if db.get_user_by_email(body.email):
        raise HTTPException(status_code=409, detail="Email sudah terdaftar")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password minimal 6 karakter")
    uid = db.create_user(
        body.username, body.email, auth.hash_password(body.password), body.full_name or body.username
    )
    token = auth.create_token(uid)
    return {"token": token, "user": {"id": uid, "username": body.username, "email": body.email}}


@app.post("/api/auth/login")
def login(body: LoginBody):
    user = db.get_user_by_email(body.email)
    if not user or not auth.verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    token = auth.create_token(user["id"])
    return {
        "token": token,
        "user": {"id": user["id"], "username": user["username"], "email": user["email"]},
    }


@app.get("/api/auth/me")
def me(user_id: str = Depends(auth.get_current_user_id)):
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    return {"id": user["id"], "username": user["username"], "email": user["email"], "full_name": user["full_name"]}


# ---------------------------------------------------------- B. DIAGNOSIS --
@app.get("/api/diagnosis/symptoms")
def list_symptoms():
    return [{"id": k, "text": v} for k, v in SYMPTOMS.items()]


@app.get("/api/diagnosis/damages")
def list_damages():
    return [{"id": k, **v} for k, v in DAMAGES.items()]


@app.post("/api/diagnosis/start")
def start_diagnosis(body: StartBody, user_id: str | None = Depends(auth.get_optional_user_id)):
    cid = db.create_consultation(user_id or body.user_id)
    first_question = engine.get_next_question({})
    return {"consultation_id": cid, "question": first_question}


@app.get("/api/diagnosis/{consultation_id}/next-question")
def next_question(consultation_id: str):
    consult = db.get_consultation(consultation_id)
    if not consult:
        raise HTTPException(status_code=404, detail="Sesi konsultasi tidak ditemukan")
    q = engine.get_next_question(consult["answers"])
    return {"question": q, "question_count": len(consult["answers"])}


@app.post("/api/diagnosis/{consultation_id}/answer")
def answer_question(consultation_id: str, body: AnswerBody):
    consult = db.get_consultation(consultation_id)
    if not consult:
        raise HTTPException(status_code=404, detail="Sesi konsultasi tidak ditemukan")
    if consult["status"] == "done":
        raise HTTPException(status_code=400, detail="Sesi konsultasi sudah selesai")
    if body.symptom_id not in SYMPTOMS:
        raise HTTPException(status_code=400, detail="symptom_id tidak dikenal")
    if body.answer_value not in VALID_ANSWERS:
        raise HTTPException(status_code=400, detail=f"answer_value harus salah satu dari {sorted(VALID_ANSWERS)}")

    answers = consult["answers"]
    answers[body.symptom_id] = body.answer_value
    history = consult["history"] + [{"symptom_id": body.symptom_id, "answer": body.answer_value}]

    conclude = engine.should_conclude(answers)
    next_q = None if conclude else engine.get_next_question(answers)

    result = None
    status = "ongoing"
    if conclude:
        result = engine.build_result(answers)
        status = "done"

    db.update_consultation(consultation_id, answers=answers, history=history, result=result, status=status)

    return {
        "question_count": len(answers),
        "finished": conclude,
        "next_question": next_q,
        "result": result,
    }


@app.post("/api/diagnosis/process")
def process_diagnosis(body: ProcessBody):
    """Alternatif: proses semua jawaban sekaligus (bukan tanya-jawab satu per satu)."""
    unknown = [sid for sid in body.symptom_ids if sid not in SYMPTOMS]
    if unknown:
        raise HTTPException(status_code=400, detail=f"symptom_id tidak dikenal: {unknown}")
    result = engine.build_result(body.symptom_ids)
    cid = body.consultation_id
    if cid:
        consult = db.get_consultation(cid)
        if consult:
            db.update_consultation(cid, answers=body.symptom_ids, result=result, status="done")
    if not result:
        return {"result": None, "message": "Gejala tidak cukup untuk menyimpulkan diagnosis"}
    return {"result": result}


@app.get("/api/diagnosis/{consultation_id}/result")
def get_result(consultation_id: str):
    consult = db.get_consultation(consultation_id)
    if not consult:
        raise HTTPException(status_code=404, detail="Sesi konsultasi tidak ditemukan")
    return {
        "consultation_id": consultation_id,
        "status": consult["status"],
        "question_count": len(consult["answers"]),
        "result": consult["result"],
    }


@app.post("/api/diagnosis/{consultation_id}/feedback")
def submit_feedback(consultation_id: str, body: FeedbackBody):
    consult = db.get_consultation(consultation_id)
    if not consult:
        raise HTTPException(status_code=404, detail="Sesi konsultasi tidak ditemukan")
    db.add_feedback(consultation_id, body.is_correct, body.actual_damage_id)
    return {"message": "Terima kasih atas feedback-nya!"}


@app.delete("/api/diagnosis/{consultation_id}")
def cancel_diagnosis(consultation_id: str):
    consult = db.get_consultation(consultation_id)
    if not consult:
        raise HTTPException(status_code=404, detail="Sesi konsultasi tidak ditemukan")
    db.update_consultation(consultation_id, status="cancelled")
    return {"message": "Sesi konsultasi dibatalkan"}


@app.get("/api/diagnosis/damages/{damage_id}/solutions")
def damage_solution(damage_id: str):
    d = DAMAGES.get(damage_id)
    if not d:
        raise HTTPException(status_code=404, detail="Kerusakan tidak ditemukan")
    return {"damage_id": damage_id, "name": d["name"], "solution": d["solution"]}


# ------------------------------------------------------ C. USER HISTORY --
@app.get("/api/user/history")
def user_history(user_id: str = Depends(auth.get_current_user_id)):
    return db.list_user_history(user_id)


# --------------------------------------------------- D. ANALYTICS (mini) --
@app.get("/api/admin/analytics/accuracy")
def accuracy_analytics():
    return db.accuracy_stats()


@app.get("/")
def health():
    return {"status": "ok", "service": "Laptop Akinator API"}
