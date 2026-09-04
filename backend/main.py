import sqlite3
from datetime import datetime
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Vitals Logging API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "vitals.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS vitals_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                bpm REAL NOT NULL,
                peak_ac REAL NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        conn.commit()

init_db()

class LogPayload(BaseModel):
    bpm: float
    peak_ac: float
    status: str

class LogRecord(BaseModel):
    id: int
    timestamp: str
    bpm: float
    peak_ac: float
    status: str

@app.get("/")
def root():
    return {"message": "Vitals Monitoring Service Online"}

@app.post("/api/log")
def create_log(entry: LogPayload):
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO vitals_log (timestamp, bpm, peak_ac, status) VALUES (?, ?, ?, ?)",
            (current_time, entry.bpm, entry.peak_ac, entry.status),
        )
        conn.commit()
    return {"status": "success", "saved_at": current_time}

@app.get("/api/logs", response_model=List[LogRecord])
def fetch_recent_logs(limit: int = 20):
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, timestamp, bpm, peak_ac, status FROM vitals_log ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]