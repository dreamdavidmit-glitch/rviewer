# rviewer — AI-Powered Learning Diagnosis

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)

> Give it a textbook. It gives you a diagnostic quiz. Track timing. Find weak points. Get a report.

rviewer is a **Claude Code skill** + **web quiz engine** that turns any study material into an interactive diagnostic test with multi-dimensional weak-point analysis.

## How It Works

```
You: "Quiz me on Chapter 5" + PDF/notes
  → Claude reads the material
  → Generates questions tailored to the content
  → Launches interactive web quiz
  → You answer with real-time timing
  → Report: accuracy, speed, streaks, weak points, mastery level
```

## Features

- **Material → Questions** — Paste any textbook, notes, or PDF. Claude generates questions on the spot. No pre-built question bank needed.
- **Interactive Web Quiz** — Browser-based quiz with real-time per-question timer (green/yellow/red), progress bar, keyboard shortcuts (A/B/C/D), hint system, skip option
- **4-Dimensional Analysis** per topic:
  1. **Accuracy** — correct vs total
  2. **Speed** — actual time vs expected time ratio
  3. **Streaks** — consecutive correct/incorrect pattern detection
  4. **Subtopics** — pinpoint exactly which concepts are weak
- **Mastery Levels** — Mastered / Proficient / Developing / Needs Review
- **HTML Report** — Visual report with topic cards, progress bars, answer timeline, personalized recommendations
- **Persistent History** — SQLite database stores all sessions for tracking improvement over time
- **Multi-Subject** — Math, English, Physics, or anything you teach it

## Quick Start

### Install the Skill

```bash
# Clone into Claude Code skills directory
git clone https://github.com/dreamdavidmit/rviewer.git ~/.claude/skills/rviewer
```

### Install Dependencies

```bash
pip install flask
```

### Run

```bash
# Start the web server
cd ~/.claude/skills/rviewer
python web_app.py
```

Then open **http://127.0.0.1:5050** in your browser.

### Use with Claude Code

Just type `/rviewer` in Claude Code, then provide your study material. Claude reads it, generates questions, writes them to the quiz engine, and tells you when to start.

## Project Structure

```
rviewer/
├── web_app.py              # Flask web server (quiz UI + API)
├── quiz_engine.py          # Quiz logic, timing, session management
├── analyzer.py             # Multi-dimensional weak-point analysis
├── report_generator.py     # HTML visualization report
├── database.py             # SQLite persistence layer
├── models.py               # Data models (dataclasses)
├── question_bank.json      # Dynamic question bank (Claude writes here)
├── templates/
│   └── quiz.html           # Web quiz UI (React-free, vanilla JS)
├── data/                   # SQLite DB (auto-created)
├── reports/                # Generated HTML reports
└── SKILL.md                # Claude Code skill definition
```

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.6+ · Flask · SQLite |
| Frontend | Vanilla HTML/CSS/JS (zero dependencies) |
| AI | Claude Code skill — generates questions from any material |
| Reports | Static HTML with CSS styling |

## CLI Commands

The project also works as a standalone CLI:

```bash
python app.py quiz      # Terminal-based quiz
python app.py history   # View past sessions
python app.py report    # View previous reports
python app.py stats     # Student statistics
```

## Adding New Subjects

Add entries to `question_bank.json`:

```json
{
  "subjects": {
    "physics": {
      "Mechanics": [
        {
          "id": "physics-mech-001",
          "topic": "Mechanics",
          "subtopic": "Newton's Laws",
          "type": "multiple_choice",
          "question": "An object at rest stays at rest unless...",
          "options": ["Newton's 1st Law", "Newton's 2nd Law", "Newton's 3rd Law", "Hooke's Law"],
          "answer": "Newton's 1st Law",
          "expected_seconds": 30,
          "difficulty": "easy",
          "hint": "Think about inertia."
        }
      ]
    }
  }
}
```

Or just tell Claude: "Add a physics question bank for mechanics" — and it writes it for you.

## License

MIT — see [LICENSE](LICENSE)

## Author

dreamdavidmit — built for students who want to know exactly what they don't know.
