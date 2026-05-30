"""Flask web server for ruflo superpower — browser-based quiz UI."""

import json
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, render_template, request, session

from database import init_db, save_session, save_answer, get_answers_for_session
from quiz_engine import load_question_bank, get_subjects, get_topics, get_questions_for_topics
from analyzer import analyze_session, generate_overall_recommendations
from report_generator import generate_html_report

app = Flask(__name__)
app.secret_key = "ruflo-superpower-secret-key-2026"

init_db()

# Build answer key lookup: question_id -> correct_answer
_answer_key = {}
def _load_answer_key():
    global _answer_key
    bank = load_question_bank()
    for subject_data in bank.get("subjects", {}).values():
        for topic_questions in subject_data.values():
            for q in topic_questions:
                _answer_key[q["id"]] = q["answer"]
_load_answer_key()


@app.route("/")
def index():
    """Main page — quiz setup."""
    subjects = get_subjects()
    all_topics = {}
    for subj in subjects:
        all_topics[subj] = get_topics(subj)
    return render_template("quiz.html", subjects=subjects, all_topics=all_topics)


@app.route("/api/start", methods=["POST"])
def api_start():
    """Start a new quiz session, return questions."""
    data = request.get_json()
    student_name = data.get("name", "Anonymous").strip()
    subject = data.get("subject", "math").strip()
    topics = data.get("topics", [])

    if not topics:
        topics = get_topics(subject)

    questions = get_questions_for_topics(subject, topics)
    if not questions:
        return jsonify({"error": "No questions found"}), 400

    session_id = uuid.uuid4().hex[:12]
    session["quiz_session_id"] = session_id
    session["quiz_name"] = student_name
    session["quiz_subject"] = subject
    session["quiz_topics"] = topics
    session["quiz_started_at"] = datetime.now().isoformat()
    session["quiz_question_ids"] = [q.question_id for q in questions]
    session["quiz_answers"] = {}

    save_session({
        "session_id": session_id,
        "student_name": student_name,
        "subject": subject,
        "topics": topics,
        "created_at": session["quiz_started_at"],
        "completed_at": None,
        "total_questions": 0,
        "correct_count": 0,
        "total_time_seconds": 0.0,
    })

    q_list = []
    for q in questions:
        q_list.append({
            "id": q.question_id,
            "topic": q.topic,
            "subtopic": q.subtopic,
            "type": q.question_type,
            "question": q.question_text,
            "options": q.options,
            "expected_seconds": q.expected_time_seconds,
            "hint": q.hint,
            "difficulty": q.difficulty,
        })

    return jsonify({
        "session_id": session_id,
        "questions": q_list,
        "total": len(q_list),
        "subject": subject,
        "topics": topics,
    })


@app.route("/api/answer", methods=["POST"])
def api_answer():
    """Record an answer for a question."""
    data = request.get_json()
    session_id = data.get("session_id")
    question_id = data.get("question_id")
    student_answer = data.get("answer", "").strip()
    actual_time = float(data.get("actual_time", 0))
    expected_time = int(data.get("expected_time", 60))
    question_text = data.get("question_text", "")
    topic = data.get("topic", "")
    subtopic = data.get("subtopic", "")
    used_hint = data.get("used_hint", False)

    # Look up correct answer from server-side key (client never sees it)
    correct_answer = _answer_key.get(question_id, "")

    if used_hint:
        actual_time += 30

    is_correct = _check(student_answer, correct_answer)

    answer_id = uuid.uuid4().hex[:16]
    save_answer({
        "answer_id": answer_id,
        "session_id": session_id,
        "question_id": question_id,
        "question_text": question_text,
        "topic": topic,
        "subtopic": subtopic,
        "student_answer": student_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct,
        "actual_time_seconds": round(actual_time, 1),
        "expected_time_seconds": expected_time,
        "recorded_at": datetime.now().isoformat(),
    })

    return jsonify({
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "answer_id": answer_id,
    })


@app.route("/api/finish", methods=["POST"])
def api_finish():
    """Finish quiz and return report URL."""
    data = request.get_json()
    session_id = data.get("session_id")
    total_time = float(data.get("total_time", 0))

    answers = get_answers_for_session(session_id)
    correct = sum(1 for a in answers if a["is_correct"])
    total = len(answers)

    save_session({
        "session_id": session_id,
        "student_name": data.get("student_name", "Anonymous"),
        "subject": data.get("subject", "math"),
        "topics": data.get("topics", []),
        "created_at": data.get("created_at", datetime.now().isoformat()),
        "completed_at": datetime.now().isoformat(),
        "total_questions": total,
        "correct_count": correct,
        "total_time_seconds": round(total_time, 1),
    })

    analyses = analyze_session(answers)
    weaknesses = [t.topic for t in analyses if t.mastery_level in ("needs_review", "developing")]
    recs = generate_overall_recommendations(analyses, total, correct, total_time)

    report_path = generate_html_report(
        session_id=session_id,
        student_name=data.get("student_name", "Anonymous"),
        subject=data.get("subject", "math"),
        total_score=correct / total * 100 if total else 0,
        total_time=total_time,
        topic_analyses=analyses,
        top_weaknesses=weaknesses,
        study_recommendations=recs,
        answers=answers,
    )

    report_file = os.path.basename(report_path)

    return jsonify({
        "score": correct,
        "total": total,
        "accuracy": round(correct / total * 100, 1) if total else 0,
        "total_time": round(total_time, 1),
        "analyses": [
            {
                "topic": t.topic,
                "accuracy": t.accuracy,
                "mastery": t.mastery_level,
                "speed_ratio": t.speed_ratio,
                "recommendation": t.recommendation,
            }
            for t in analyses
        ],
        "recommendations": recs,
        "report_url": f"/reports/{report_file}",
    })


@app.route("/reports/<filename>")
def serve_report(filename):
    """Serve a generated report."""
    from flask import send_from_directory
    return send_from_directory("reports", filename)


def _check(student: str, correct: str) -> bool:
    s = student.strip().lower().replace(" ", "")
    c = correct.strip().lower().replace(" ", "")
    if s == c:
        return True
    try:
        return abs(float(s) - float(c)) < 0.01
    except (ValueError, TypeError):
        pass
    return False


if __name__ == "__main__":
    print("\n  ruflo superpower — Web UI")
    print("  Open http://127.0.0.1:5050 in your browser\n")
    app.run(host="127.0.0.1", port=5050, debug=False)
