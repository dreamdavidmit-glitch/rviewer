"""HTML report generator with interactive visualizations."""

import os
import webbrowser
from datetime import datetime
from typing import List

from models import TopicAnalysis


REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")


def generate_html_report(
    session_id: str,
    student_name: str,
    subject: str,
    total_score: float,
    total_time: float,
    topic_analyses: List[TopicAnalysis],
    top_weaknesses: List[str],
    study_recommendations: List[str],
    answers: List[dict],
) -> str:
    """Generate interactive HTML report and return file path."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    filename = f"report_{session_id}.html"
    filepath = os.path.join(REPORT_DIR, filename)

    accuracy = total_score if total_score <= 1 else total_score / 100

    # Build topic cards
    topic_cards = ""
    for t in topic_analyses:
        level_color = {
            "mastered": "#22c55e",
            "proficient": "#3b82f6",
            "developing": "#f59e0b",
            "needs_review": "#ef4444",
        }.get(t.mastery_level, "#6b7280")

        weak_list = "".join(f'<span class="tag weak">{st}</span>' for st in t.weak_subtopics)

        topic_cards += f"""
        <div class="topic-card" style="border-left: 4px solid {level_color}">
            <div class="topic-header">
                <h3>{t.topic}</h3>
                <span class="mastery-badge" style="background:{level_color}">{t.mastery_level.replace('_', ' ').title()}</span>
            </div>
            <div class="topic-metrics">
                <div class="metric">
                    <div class="metric-value">{t.accuracy:.0f}%</div>
                    <div class="metric-label">Accuracy</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{t.speed_ratio:.1f}x</div>
                    <div class="metric-label">Speed vs Expected</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{t.correct_count}/{t.total_questions}</div>
                    <div class="metric-label">Correct / Total</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{t.avg_actual_time:.0f}s</div>
                    <div class="metric-label">Avg Time (expected {t.avg_expected_time:.0f}s)</div>
                </div>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width:{t.accuracy}%;background:{level_color}"></div>
            </div>
            {f'<div class="weak-subtopics">{weak_list}</div>' if weak_list else ''}
            <div class="recommendation">{t.recommendation}</div>
        </div>
        """

    # Build answer timeline
    answer_rows = ""
    for i, a in enumerate(answers, 1):
        icon = "correct" if a["is_correct"] else "wrong"
        emoji = "+" if a["is_correct"] else "-"
        time_diff = a["actual_time_seconds"] - a["expected_time_seconds"]
        time_class = "time-fast" if time_diff < -5 else ("time-slow" if time_diff > 15 else "time-ok")
        time_note = f"{time_diff:+.0f}s" if abs(time_diff) > 3 else "on pace"
        answer_rows += f"""
        <tr class="answer-row {icon}">
            <td>{i}</td>
            <td><span class="topic-tag">{a['topic']}</span></td>
            <td>{a['subtopic']}</td>
            <td class="q-text">{a['question_text'][:60]}...</td>
            <td class="student-ans">{a['student_answer']}</td>
            <td class="correct-ans">{a['correct_answer']}</td>
            <td class="result-icon">{emoji}</td>
            <td class="{time_class}">{a['actual_time_seconds']}s ({time_note})</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Learning Diagnosis Report — {student_name}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.6; }}
.container {{ max-width: 1100px; margin: 0 auto; padding: 20px; }}

.header {{ background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%); color: white; padding: 40px; border-radius: 16px; margin-bottom: 24px; }}
.header h1 {{ font-size: 28px; margin-bottom: 8px; }}
.header .subtitle {{ opacity: 0.85; font-size: 14px; }}
.header .meta {{ display: flex; gap: 30px; margin-top: 20px; flex-wrap: wrap; }}
.header .meta-item {{ text-align: center; }}
.header .meta-item .big {{ font-size: 32px; font-weight: 700; }}
.header .meta-item .label {{ font-size: 12px; opacity: 0.7; text-transform: uppercase; letter-spacing: 1px; }}

.accuracy-circle {{ width: 120px; height: 120px; border-radius: 50%; border: 8px solid #22c55e; display: flex; align-items: center; justify-content: center; font-size: 36px; font-weight: 700; margin: 0 auto; }}
.accuracy-circle.warn {{ border-color: #f59e0b; }}
.accuracy-circle.danger {{ border-color: #ef4444; }}

.recommendations {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
.recommendations h2 {{ font-size: 18px; margin-bottom: 12px; color: #1e3a5f; }}
.recommendations ul {{ padding-left: 20px; }}
.recommendations li {{ margin-bottom: 8px; font-size: 14px; }}

.topic-card {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
.topic-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
.topic-header h3 {{ font-size: 17px; }}
.mastery-badge {{ color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase; }}
.topic-metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 12px; }}
.metric {{ text-align: center; }}
.metric-value {{ font-size: 22px; font-weight: 700; }}
.metric-label {{ font-size: 11px; color: #64748b; text-transform: uppercase; }}
.progress-bar-bg {{ height: 8px; background: #e2e8f0; border-radius: 4px; margin-bottom: 10px; overflow: hidden; }}
.progress-bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.6s ease; }}
.weak-subtopics {{ margin-bottom: 8px; }}
.tag {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 13px; margin-right: 6px; }}
.tag.weak {{ background: #fef2f2; color: #dc2626; }}
.recommendation {{ font-size: 13px; color: #475569; font-style: italic; }}

table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 24px; }}
th {{ background: #f1f5f9; padding: 12px; text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; }}
td {{ padding: 10px 12px; font-size: 13px; border-top: 1px solid #f1f5f9; }}
.answer-row.correct {{ border-left: 3px solid #22c55e; }}
.answer-row.wrong {{ border-left: 3px solid #ef4444; }}
.topic-tag {{ background: #eff6ff; color: #2563eb; padding: 2px 10px; border-radius: 10px; font-size: 13px; }}
.result-icon {{ font-size: 18px; font-weight: 700; text-align: center; }}
.time-fast {{ color: #22c55e; }} .time-slow {{ color: #ef4444; }} .time-ok {{ color: #64748b; }}

.footer {{ text-align: center; color: #94a3b8; font-size: 12px; margin: 40px 0 20px; }}

@media (max-width: 768px) {{
    .topic-metrics {{ grid-template-columns: repeat(2, 1fr); }}
    .header .meta {{ gap: 15px; }}
}}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>Learning Diagnosis Report</h1>
        <div class="subtitle">AI-Powered Weak Point Analysis — ruflo superpower</div>
        <div class="meta">
            <div class="meta-item">
                <div class="big">{total_score:.0f}%</div>
                <div class="label">Overall Score</div>
            </div>
            <div class="meta-item">
                <div class="big">{total_time/60:.1f}m</div>
                <div class="label">Total Time</div>
            </div>
            <div class="meta-item">
                <div class="big">{student_name}</div>
                <div class="label">Student</div>
            </div>
            <div class="meta-item">
                <div class="big">{subject.title()}</div>
                <div class="label">Subject</div>
            </div>
            <div class="meta-item">
                <div class="big">{len(answers)}</div>
                <div class="label">Questions</div>
            </div>
        </div>
    </div>

    <div class="recommendations">
        <h2>Top Study Recommendations</h2>
        <ul>
            {''.join(f'<li>{r}</li>' for r in study_recommendations)}
        </ul>
    </div>

    <h2 style="font-size:20px;margin-bottom:16px;">Topic Analysis</h2>
    {topic_cards}

    <h2 style="font-size:20px;margin:24px 0 16px;">Answer Timeline</h2>
    <div style="overflow-x:auto;">
    <table>
        <thead>
            <tr><th>#</th><th>Topic</th><th>Subtopic</th><th>Question</th><th>Your Answer</th><th>Correct</th><th></th><th>Time</th></tr>
        </thead>
        <tbody>{answer_rows}</tbody>
    </table>
    </div>

    <div class="footer">
        Generated by ruflo superpower AI Learning Diagnosis System &mdash; {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
</div>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return filepath


def open_report(filepath: str):
    """Open report in default browser."""
    abs_path = os.path.abspath(filepath)
    webbrowser.open(f"file:///{abs_path}")
