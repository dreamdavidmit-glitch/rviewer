"""Quiz engine with real-time answer timing and session management."""

import json
import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from database import save_session, save_answer, get_answers_for_session, get_db
from models import Question, QuizSession

QB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "question_bank.json")


def load_question_bank() -> dict:
    with open(QB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_subjects() -> List[str]:
    bank = load_question_bank()
    return list(bank.get("subjects", {}).keys())


def get_topics(subject: str) -> List[str]:
    bank = load_question_bank()
    return list(bank.get("subjects", {}).get(subject, {}).keys())


def get_questions_for_topics(subject: str, topics: List[str]) -> List[Question]:
    bank = load_question_bank()
    questions: List[Question] = []
    subject_data = bank.get("subjects", {}).get(subject, {})
    for topic in topics:
        raw_list = subject_data.get(topic, [])
        for raw in raw_list:
            q = Question(
                question_id=raw["id"],
                subject=subject,
                topic=raw["topic"],
                subtopic=raw["subtopic"],
                question_type=raw["type"],
                question_text=raw["question"],
                options=raw.get("options", []),
                correct_answer=raw["answer"],
                expected_time_seconds=raw["expected_seconds"],
                difficulty=raw.get("difficulty", "medium"),
                hint=raw.get("hint", ""),
            )
            questions.append(q)
    return questions


def create_quiz_session(student_name: str, subject: str, topics: List[str]) -> QuizSession:
    session_id = uuid.uuid4().hex[:12]
    session = QuizSession(
        session_id=session_id,
        student_name=student_name.strip(),
        subject=subject,
        topics=topics,
        created_at=datetime.now().isoformat(),
        total_questions=0,
        correct_count=0,
        total_time_seconds=0.0,
    )
    save_session({
        "session_id": session.session_id,
        "student_name": session.student_name,
        "subject": session.subject,
        "topics": session.topics,
        "created_at": session.created_at,
        "completed_at": None,
        "total_questions": 0,
        "correct_count": 0,
        "total_time_seconds": 0.0,
    })
    return session


def run_quiz(session: QuizSession, questions: List[Question]) -> Tuple[int, int, float]:
    """Run interactive quiz. Returns (correct_count, total, total_time)."""
    correct = 0
    total_time = 0.0

    print(f"\n{'='*60}")
    print(f"  Subject: {session.subject.upper()}  |  Student: {session.student_name}")
    print(f"  Topics: {', '.join(session.topics)}")
    print(f"  Questions: {len(questions)}")
    print(f"{'='*60}")
    print("  Type 'hint' to get a hint (costs time penalty)")
    print("  Type 'skip' to skip (marked wrong, records 0 time)")
    print(f"{'='*60}\n")

    for i, q in enumerate(questions, 1):
        print(f"--- Q{i}/{len(questions)} [{q.topic}] [{q.subtopic}] [{q.expected_time_seconds}s expected] ---")
        print(f"  {q.question_text}")

        if q.options:
            letters = "abcd"
            for j, opt in enumerate(q.options):
                print(f"    {letters[j]}) {opt}")

        start_time = time.time()
        raw_answer = input("  Your answer: ").strip()
        elapsed = round(time.time() - start_time, 1)

        if raw_answer.lower() == "hint":
            print(f"  [HINT] {q.hint}")
            print(f"  [PENALTY] +30s time penalty for using hint")
            start_time2 = time.time()
            raw_answer = input("  Your answer: ").strip()
            elapsed = round(elapsed + time.time() - start_time2 + 30, 1)

        if raw_answer.lower() == "skip":
            print(f"  [SKIPPED] Answer was: {q.correct_answer}")
            elapsed = 0.0
            raw_answer = "[SKIPPED]"

        if q.options and raw_answer.lower() in "abcd":
            idx = ord(raw_answer.lower()) - ord("a")
            if 0 <= idx < len(q.options):
                raw_answer = q.options[idx]

        is_correct = _check_answer(raw_answer, q.correct_answer, q.question_type)

        if is_correct:
            print(f"  [CORRECT] ({elapsed}s)")
            correct += 1
        else:
            print(f"  [WRONG] Answer: {q.correct_answer} ({elapsed}s)")

        total_time += elapsed

        save_answer({
            "answer_id": uuid.uuid4().hex[:16],
            "session_id": session.session_id,
            "question_id": q.question_id,
            "question_text": q.question_text,
            "topic": q.topic,
            "subtopic": q.subtopic,
            "student_answer": raw_answer,
            "correct_answer": q.correct_answer,
            "is_correct": is_correct,
            "actual_time_seconds": elapsed,
            "expected_time_seconds": q.expected_time_seconds,
            "recorded_at": datetime.now().isoformat(),
        })
        print()

    session.completed_at = datetime.now().isoformat()
    session.total_questions = len(questions)
    session.correct_count = correct
    session.total_time_seconds = round(total_time, 1)

    save_session({
        "session_id": session.session_id,
        "student_name": session.student_name,
        "subject": session.subject,
        "topics": session.topics,
        "created_at": session.created_at,
        "completed_at": session.completed_at,
        "total_questions": session.total_questions,
        "correct_count": session.correct_count,
        "total_time_seconds": session.total_time_seconds,
    })

    return correct, len(questions), total_time


def _check_answer(student: str, correct: str, qtype: str) -> bool:
    """Compare student answer to correct answer."""
    s = student.strip().lower().replace(" ", "")
    c = correct.strip().lower().replace(" ", "")

    if s == c:
        return True
    if s.replace("^", "**") == c.replace("^", "**"):
        return True

    try:
        sf = float(s)
        cf = float(c)
        return abs(sf - cf) < 0.01
    except (ValueError, TypeError):
        pass

    return False
