"""SQLite database layer for persistent storage of quiz data."""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "quiz_data.db")


def get_db() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS quiz_sessions (
            session_id TEXT PRIMARY KEY,
            student_name TEXT NOT NULL,
            subject TEXT NOT NULL,
            topics TEXT NOT NULL,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            total_questions INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            total_time_seconds REAL DEFAULT 0.0
        );

        CREATE TABLE IF NOT EXISTS answers (
            answer_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            question_text TEXT NOT NULL,
            topic TEXT NOT NULL,
            subtopic TEXT NOT NULL,
            student_answer TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            actual_time_seconds REAL NOT NULL,
            expected_time_seconds INTEGER NOT NULL,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES quiz_sessions(session_id)
        );

        CREATE INDEX IF NOT EXISTS idx_answers_session ON answers(session_id);
        CREATE INDEX IF NOT EXISTS idx_answers_topic ON answers(topic);
        CREATE INDEX IF NOT EXISTS idx_answers_subtopic ON answers(subtopic);
    """)
    conn.commit()
    conn.close()


def save_session(data: dict):
    conn = get_db()
    conn.execute("""
        INSERT OR REPLACE INTO quiz_sessions
        (session_id, student_name, subject, topics, created_at, completed_at,
         total_questions, correct_count, total_time_seconds)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["session_id"], data["student_name"], data["subject"],
        ",".join(data["topics"]), data["created_at"], data.get("completed_at"),
        data.get("total_questions", 0), data.get("correct_count", 0),
        data.get("total_time_seconds", 0.0)
    ))
    conn.commit()
    conn.close()


def save_answer(data: dict):
    conn = get_db()
    conn.execute("""
        INSERT INTO answers
        (answer_id, session_id, question_id, question_text, topic, subtopic,
         student_answer, correct_answer, is_correct, actual_time_seconds,
         expected_time_seconds, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["answer_id"], data["session_id"], data["question_id"],
        data["question_text"], data["topic"], data["subtopic"],
        data["student_answer"], data["correct_answer"],
        1 if data["is_correct"] else 0, data["actual_time_seconds"],
        data["expected_time_seconds"], data["recorded_at"]
    ))
    conn.commit()
    conn.close()


def get_session(session_id: str) -> Optional[dict]:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM quiz_sessions WHERE session_id = ?", (session_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def get_answers_for_session(session_id: str) -> List[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM answers WHERE session_id = ? ORDER BY recorded_at",
        (session_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_sessions(subject: Optional[str] = None) -> List[dict]:
    conn = get_db()
    if subject:
        rows = conn.execute(
            "SELECT * FROM quiz_sessions WHERE subject = ? ORDER BY created_at DESC",
            (subject,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM quiz_sessions ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_topic_history(topic: str, student_name: str) -> List[dict]:
    conn = get_db()
    rows = conn.execute("""
        SELECT a.* FROM answers a
        JOIN quiz_sessions s ON a.session_id = s.session_id
        WHERE a.topic = ? AND s.student_name = ?
        ORDER BY a.recorded_at DESC
    """, (topic, student_name)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_student_stats(student_name: str) -> dict:
    conn = get_db()
    sessions = conn.execute(
        "SELECT COUNT(*) as total_sessions, "
        "AVG(correct_count * 100.0 / CASE WHEN total_questions = 0 THEN 1 ELSE total_questions END) as avg_accuracy, "
        "SUM(total_time_seconds) as total_time "
        "FROM quiz_sessions WHERE student_name = ?",
        (student_name,)
    ).fetchone()
    conn.close()
    return {
        "total_sessions": sessions["total_sessions"],
        "avg_accuracy": round(sessions["avg_accuracy"] or 0, 1),
        "total_study_time": round((sessions["total_time"] or 0) / 60, 1)
    }
