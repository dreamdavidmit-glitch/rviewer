#!/usr/bin/env python
"""
ruflo superpower — AI Learning Diagnosis System
================================================
A multi-dimensional quiz engine that tracks answer timing,
analyzes weak knowledge points, and generates visual reports.

Usage:
    python app.py quiz        Start a new quiz session
    python app.py report      View recent report
    python app.py history     View quiz history
    python app.py stats       View student statistics
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import (
    init_db, get_session, get_answers_for_session,
    get_all_sessions, get_student_stats,
)
from quiz_engine import (
    load_question_bank, get_subjects, get_topics,
    get_questions_for_topics, create_quiz_session, run_quiz,
)
from analyzer import analyze_session, generate_overall_recommendations
from report_generator import generate_html_report, open_report


def cmd_quiz():
    """Interactive quiz flow."""
    print("\n" + "=" * 60)
    print("  ruflo superpower — AI Learning Diagnosis System")
    print("=" * 60)

    # Get student name
    name = input("\n  Student name: ").strip()
    if not name:
        name = "Anonymous"

    # Choose subject
    subjects = get_subjects()
    print(f"\n  Available subjects: {', '.join(subjects)}")
    subject = input("  Subject: ").strip().lower()
    if subject not in subjects:
        print(f"  Invalid subject. Using '{subjects[0]}'")
        subject = subjects[0]

    # Choose topics
    topics = get_topics(subject)
    print(f"\n  Available topics for {subject}:")
    for i, t in enumerate(topics, 1):
        print(f"    {i}. {t}")
    print(f"    a. All topics")
    choice = input("  Select (number or 'a'): ").strip().lower()

    if choice == "a":
        selected = topics
    else:
        try:
            indices = [int(c.strip()) - 1 for c in choice.split(",")]
            selected = [topics[i] for i in indices if 0 <= i < len(topics)]
        except (ValueError, IndexError):
            print("  Invalid selection. Using all topics.")
            selected = topics

    if not selected:
        selected = topics

    # Load questions
    questions = get_questions_for_topics(subject, selected)
    if not questions:
        print(f"  No questions found for {selected} in {subject}.")
        return

    # Create session & run quiz
    session = create_quiz_session(name, subject, selected)
    correct, total, total_time = run_quiz(session, questions)

    # Analyze
    print(f"\n{'='*60}")
    print(f"  Quiz Complete!")
    print(f"  Score: {correct}/{total} ({correct/total*100:.0f}%)")
    print(f"  Time: {total_time:.0f}s ({total_time/60:.1f} min)")
    print(f"{'='*60}")

    answers = get_answers_for_session(session.session_id)
    topic_analyses = analyze_session(answers)

    # Determine weaknesses
    weaknesses = [
        t.topic for t in topic_analyses
        if t.mastery_level in ("needs_review", "developing")
    ]
    if not weaknesses:
        weaknesses = [t.topic for t in topic_analyses if t.accuracy < 80]

    recommendations = generate_overall_recommendations(
        topic_analyses, total, correct, total_time
    )

    # Generate report
    report_path = generate_html_report(
        session_id=session.session_id,
        student_name=name,
        subject=subject,
        total_score=correct/total*100,
        total_time=total_time,
        topic_analyses=topic_analyses,
        top_weaknesses=weaknesses,
        study_recommendations=recommendations,
        answers=answers,
    )

    print(f"\n  Report generated: {report_path}")

    view = input("  Open report in browser? (y/n): ").strip().lower()
    if view == "y":
        open_report(report_path)
        print("  Opening in browser...")


def cmd_report():
    """View the most recent report."""
    sessions = get_all_sessions()
    if not sessions:
        print("No quiz sessions found. Run 'python app.py quiz' first.")
        return

    print("\nRecent sessions:")
    for i, s in enumerate(sessions[:10], 1):
        acc = s["correct_count"] / s["total_questions"] * 100 if s["total_questions"] else 0
        print(f"  {i}. [{s['subject']}] {s['student_name']} — "
              f"{s['correct_count']}/{s['total_questions']} ({acc:.0f}%) — "
              f"{s['created_at'][:10]}")

    choice = input("\n  Select session number (or Enter to cancel): ").strip()
    if not choice:
        return

    try:
        idx = int(choice) - 1
        session = sessions[idx]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    # Rebuild report
    answers = get_answers_for_session(session["session_id"])
    topic_analyses = analyze_session(answers)
    total = session["total_questions"]
    correct = session["correct_count"]
    total_time = session["total_time_seconds"]
    weaknesses = [t.topic for t in topic_analyses if t.mastery_level in ("needs_review", "developing")]
    recommendations = generate_overall_recommendations(topic_analyses, total, correct, total_time)

    report_path = generate_html_report(
        session_id=session["session_id"],
        student_name=session["student_name"],
        subject=session["subject"],
        total_score=correct/total*100 if total else 0,
        total_time=total_time,
        topic_analyses=topic_analyses,
        top_weaknesses=weaknesses,
        study_recommendations=recommendations,
        answers=answers,
    )
    open_report(report_path)
    print(f"Report opened: {report_path}")


def cmd_history():
    """Show quiz history."""
    sessions = get_all_sessions()
    if not sessions:
        print("No quiz sessions found.")
        return

    print(f"\n{'='*70}")
    print(f"  Quiz History ({len(sessions)} sessions)")
    print(f"{'='*70}")
    for s in sessions:
        acc = s["correct_count"] / s["total_questions"] * 100 if s["total_questions"] else 0
        emoji = "high_brightness" if acc >= 80 else ("warning" if acc >= 60 else "police_car_light")
        topics = s.get("topics", "all")
        print(f"  [{s['created_at'][:10]}] {s['student_name']:12s} | {s['subject']:8s} | "
              f"{s['correct_count']}/{s['total_questions']} ({acc:5.1f}%) | "
              f"{s['total_time_seconds']/60:5.1f}m | {topics}")


def cmd_stats():
    """Show student statistics."""
    name = input("Student name: ").strip()
    if not name:
        print("Please provide a student name.")
        return

    stats = get_student_stats(name)
    if stats["total_sessions"] == 0:
        print(f"No data found for '{name}'.")
        return

    print(f"\n{'='*50}")
    print(f"  Statistics for: {name}")
    print(f"{'='*50}")
    print(f"  Total sessions:     {stats['total_sessions']}")
    print(f"  Average accuracy:   {stats['avg_accuracy']}%")
    print(f"  Total study time:   {stats['total_study_time']} min")
    print(f"{'='*50}")


def main():
    init_db()

    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()

    if cmd == "quiz":
        cmd_quiz()
    elif cmd == "report":
        cmd_report()
    elif cmd == "history":
        cmd_history()
    elif cmd == "stats":
        cmd_stats()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
