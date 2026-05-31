# rviewer — AI Learning Diagnosis Claude Skill

<p align="center">
  <img src="https://img.shields.io/badge/Claude_Skill-Installed-8b5cf6?logo=anthropic" alt="Claude Skill">
  <img src="https://img.shields.io/badge/Claude_Code-Compatible-3b82f6?logo=claude" alt="Claude Code">
  <img src="https://img.shields.io/badge/MCP_Ready-22c55e" alt="MCP Ready">
  <img src="https://img.shields.io/badge/Python-3.6+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <a href="https://github.com/dreamdavidmit-glitch/rviewer/stargazers"><img src="https://img.shields.io/github/stars/dreamdavidmit-glitch/rviewer?style=social" alt="Stars"></a>
</p>

<p align="center">
  <b>Drop in a textbook. Get a diagnostic quiz. Find your weak points. Fix them.</b>
</p>

> **rviewer** is an open-source Claude Code skill that turns ANY study material into an interactive diagnostic quiz with real-time timing, multi-dimensional weak-point analysis, and a visual mastery report — all in your browser.

---

## Why rviewer?

Most AI quiz tools give you generic questions. **rviewer reads YOUR material** — your textbook chapter, your class notes, your PDF — and generates questions tailored to exactly what you're studying. Then it tracks how fast you answer, spots patterns in your mistakes, and tells you what to review.

| | Traditional Quiz Apps | rviewer |
|---|---|---|
| Question source | Pre-built generic bank | **Generated from YOUR material** |
| Timing analysis | None | **Per-question real-time tracking** |
| Weak point detection | Correct/wrong only | **4D: accuracy + speed + streaks + subtopics** |
| Delivery | App download | **Browser + Claude Code skill** |
| Subjects | Fixed | **Anything you teach it** |

## Quick Demo

```
You: "/rviewer — quiz me on Math 10 Unit 5"
Claude: reads your Obsidian notes → generates 20 Quadratic Functions questions
You: open http://127.0.0.1:5050 → take the quiz → instant mastery report
```

## Features

### Claude Code Skill
- **/rviewer** command — invoke from any Claude Code session
- Reads material from PDF, screenshots, Obsidian vault, or pasted text
- Claude generates fresh questions every time — no stale question banks
- Server-side answer key — student never sees correct answers

### Interactive Web Quiz
- Real-time per-question timer: green → yellow → red as time runs out
- Keyboard shortcuts (A/B/C/D for multiple choice, Enter for fill-in)
- Hint system with time penalty (+30s)
- Skip option — marked wrong but records 0s time
- Progress bar + immediate correct/wrong feedback

### 4-Dimensional Analysis Per Topic

| Dimension | What It Measures | Weight |
|-----------|-----------------|--------|
| **Accuracy** | Correct / Total | 40% |
| **Speed** | Actual time vs Expected time ratio | 30% |
| **Streaks** | Longest consecutive correct answers | 30% |
| **Subtopics** | Pinpoint exactly which concepts are weak | — |

### Mastery Levels
- **Mastered** (85+) → Move on to harder material
- **Proficient** (65-84) → Minor gaps, targeted practice
- **Developing** (40-64) → Needs focused review
- **Needs Review** (<40) → Urgent: revisit fundamentals

### HTML Diagnostic Report
- Topic cards with color-coded mastery badges
- Progress bars for each topic
- Complete answer timeline (what you answered vs correct answer vs time taken)
- Personalized study recommendations
- One-click open in browser

### Persistent History
- SQLite database stores every session
- Track improvement over days/weeks
- `python app.py stats` — see your average accuracy and total study time

---

## Install

### Option 1: Claude Code Skill (Recommended)

```bash
# Clone into your Claude Code skills directory
git clone https://github.com/dreamdavidmit-glitch/rviewer.git ~/.claude/skills/rviewer
```

Then restart Claude Code — `/rviewer` will be available.

### Option 2: Standalone Web App

```bash
git clone https://github.com/dreamdavidmit-glitch/rviewer.git
cd rviewer
pip install flask
python web_app.py
# Open http://127.0.0.1:5050
```

### Option 3: CLI Only (No Browser)

```bash
python app.py quiz      # Terminal-based quiz
python app.py history   # View past sessions
python app.py report    # Reopen previous reports
python app.py stats     # Your statistics
```

---

## Tech Stack

| Layer | Choice |
|-------|--------|
| AI / Skill | Claude Code (Anthropic) |
| Backend | Python 3.6+ · Flask |
| Frontend | Vanilla HTML/CSS/JS — zero npm dependencies |
| Database | SQLite + WAL mode |
| Reports | Static HTML with CSS (no JS framework) |

**Zero frontend build step. Zero npm install. Just Python + a browser.**

---

## Project Structure

```
rviewer/
├── SKILL.md                # Claude Code skill definition
├── web_app.py              # Flask server (quiz API + report serving)
├── quiz_engine.py          # Quiz logic, real-time timing, session mgmt
├── analyzer.py             # 4D weak-point analysis engine
├── report_generator.py     # HTML visualization report generator
├── database.py             # SQLite persistence with WAL
├── models.py               # Python dataclasses + enums
├── question_bank.json      # Dynamic question bank (Claude writes here)
├── templates/
│   └── quiz.html           # Interactive quiz UI
├── app.py                  # CLI entry point (quiz/history/report/stats)
├── data/                   # SQLite DB (auto-created at runtime)
└── reports/                # Generated HTML diagnostic reports
```

---

## How It Works (Architecture)

```
┌─────────────────────────────────────────────────────────┐
│  Claude Code (AI)                                       │
│  Reads your material → Generates questions → JSON       │
└──────────────────────┬──────────────────────────────────┘
                       │ writes to
                       ▼
┌─────────────────────────────────────────────────────────┐
│  question_bank.json                                     │
│  Dynamic — rebuilt every time you quiz a new topic      │
└──────────────────────┬──────────────────────────────────┘
                       │ loaded by
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Flask Web Server (web_app.py)                          │
│  /api/start  → new session + questions                  │
│  /api/answer → check answer (server-side key)           │
│  /api/finish → analysis + report                        │
└──────────────────────┬──────────────────────────────────┘
                       │ serves
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Browser Quiz UI (quiz.html)                            │
│  Real-time timer · Keyboard shortcuts · Live feedback   │
└─────────────────────────────────────────────────────────┘
```

---

## Adding Your Own Subjects

Edit `question_bank.json` — or just tell Claude:

> "Add a physics question bank for Newtonian Mechanics"

Claude writes the JSON for you. Example structure:

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
          "question": "An object at rest stays at rest unless acted upon by...",
          "options": ["An unbalanced force", "Gravity only", "Friction only", "Its own weight"],
          "answer": "An unbalanced force",
          "expected_seconds": 30,
          "difficulty": "easy",
          "hint": "This is Newton's First Law — the law of inertia."
        }
      ]
    }
  }
}
```

---

## Keywords

`claude-skill` `claude-code` `claude-code-skill` `mcp` `mcp-server` `ai-agent` `ai-learning` `ai-education` `edtech` `anthropic` `claude` `diagnostic-quiz` `learning-analytics` `self-study` `quiz-generator` `weak-point-analysis` `study-tool` `ai-tutor` `open-source` `python` `flask`

---

## Star History

If this project helped you study, consider giving it a ⭐ — it helps other students find it too.

---

## License

MIT — see [LICENSE](LICENSE)

## Author

**dreamdavidmit** — student, builder, Claude Code enthusiast.

*"Built this because I was tired of guessing what I didn't know."*
