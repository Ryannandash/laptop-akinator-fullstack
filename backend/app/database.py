import sqlite3
import os
import json
import time
import uuid

# Di Vercel, filesystem yang bisa ditulis hanya /tmp (ephemeral per instance).
# Untuk kebutuhan tugas ini itu cukup: data user & histori tetap ada selama
# instance masih "hangat". Kalau butuh histori permanen lintas deploy,
# tinggal ganti DB_PATH ini ke Postgres (mis. Vercel Postgres / Supabase).
DB_PATH = os.environ.get("DB_PATH", "/tmp/akinator.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT,
            email TEXT UNIQUE,
            password_hash TEXT,
            full_name TEXT,
            created_at REAL
        );
        CREATE TABLE IF NOT EXISTS consultations (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            answers TEXT DEFAULT '{}',
            history TEXT DEFAULT '[]',
            result TEXT,
            status TEXT DEFAULT 'ongoing',
            created_at REAL
        );
        CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY,
            consultation_id TEXT,
            is_correct INTEGER,
            actual_damage_id TEXT,
            created_at REAL
        );
        """
    )
    conn.commit()
    conn.close()


# ---------- users ----------
def create_user(username, email, password_hash, full_name):
    uid = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        "INSERT INTO users (id, username, email, password_hash, full_name, created_at) VALUES (?,?,?,?,?,?)",
        (uid, username, email, password_hash, full_name, time.time()),
    )
    conn.commit()
    conn.close()
    return uid


def get_user_by_email(email):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(uid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------- consultations ----------
def create_consultation(user_id):
    cid = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        "INSERT INTO consultations (id, user_id, answers, history, created_at) VALUES (?,?,?,?,?)",
        (cid, user_id, "{}", "[]", time.time()),
    )
    conn.commit()
    conn.close()
    return cid


def get_consultation(cid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM consultations WHERE id = ?", (cid,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["answers"] = json.loads(d["answers"])
    d["history"] = json.loads(d["history"])
    if d["result"]:
        d["result"] = json.loads(d["result"])
    return d


def update_consultation(cid, answers=None, history=None, result=None, status=None):
    fields, values = [], []
    if answers is not None:
        fields.append("answers = ?")
        values.append(json.dumps(answers))
    if history is not None:
        fields.append("history = ?")
        values.append(json.dumps(history))
    if result is not None:
        fields.append("result = ?")
        values.append(json.dumps(result))
    if status is not None:
        fields.append("status = ?")
        values.append(status)
    if not fields:
        return
    values.append(cid)
    conn = get_conn()
    conn.execute(f"UPDATE consultations SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    conn.close()


def list_user_history(user_id, limit=20):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM consultations WHERE user_id = ? AND status = 'done' ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["result"] = json.loads(d["result"]) if d["result"] else None
        out.append(d)
    return out


# ---------- feedback ----------
def add_feedback(consultation_id, is_correct, actual_damage_id):
    fid = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        "INSERT INTO feedback (id, consultation_id, is_correct, actual_damage_id, created_at) VALUES (?,?,?,?,?)",
        (fid, consultation_id, 1 if is_correct else 0, actual_damage_id, time.time()),
    )
    conn.commit()
    conn.close()
    return fid


def accuracy_stats():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) c FROM feedback").fetchone()["c"]
    correct = conn.execute("SELECT COUNT(*) c FROM feedback WHERE is_correct = 1").fetchone()["c"]
    conn.close()
    rate = round((correct / total) * 100, 1) if total else None
    return {"total_feedback": total, "correct": correct, "accuracy_rate": rate}
