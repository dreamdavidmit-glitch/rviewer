# ruflo superpower — AI Learning Diagnosis Skill

A flexible diagnostic quiz skill. Give Claude any textbook, chapter notes, or study material — Claude generates tailored questions, launches an interactive web quiz with timing, and produces a multi-dimensional weak-point analysis report.

## When to Use

- User says "quiz me on this", "test my understanding", "create a diagnostic test"
- User provides study material and wants to check mastery
- User wants to find weak points in a specific subject/topic
- "帮我出题", "测验一下", "诊断我的掌握程度"

## Workflow

### Step 1: Receive Material

User provides study material in any form:
- PDF textbook chapter
- Screenshots/images of notes or textbook pages
- Pasted text (syllabus, notes, textbook excerpt)
- Obsidian vault notes
- "Unit 5 Quadratic Functions" — Claude finds it in Obsidian

### Step 2: Read & Understand

Read the material thoroughly. Identify:
- Main topics and subtopics
- Key concepts, formulas, definitions
- Types of problems covered
- Difficulty range

### Step 3: Generate Questions

Generate questions directly in the chat, following this format for EACH question:

```
Q:[topic]|[subtopic]|[type]|[difficulty]|[expected_seconds]
[question text]
A: [correct answer]
Options: [option1] | [option2] | [option3] | [option4]   (for MC only)
H: [hint]
```

Rules for question generation:
- Cover ALL topics in the material
- Mix difficulties: 30% easy, 50% medium, 20% hard
- Mix types: multiple_choice and fill_blank
- At least 2 questions per subtopic
- 8-24 questions total depending on material size
- expected_seconds: easy=30-60s, medium=60-120s, hard=120-200s
- Every question MUST have a hint

### Step 4: Write Question Bank

Write ALL generated questions into the quiz engine's question bank file:
`L:\project(AI review helper)\question_bank.json`

Use the exact JSON structure:
```json
{
  "subjects": {
    "<subject>": {
      "<topic>": [
        {
          "id": "<subject>-<topic_slug>-<number>",
          "topic": "<Topic Name>",
          "subtopic": "<Subtopic Name>",
          "type": "multiple_choice",
          "question": "<Full question text>",
          "options": ["<A>", "<B>", "<C>", "<D>"],
          "answer": "<Correct answer>",
          "expected_seconds": 90,
          "difficulty": "medium",
          "hint": "<Helpful hint>"
        }
      ]
    }
  }
}
```

For fill_blank questions, use `"options": []`.

### Step 5: Launch Quiz

Start the web server (only if not already running):

```bash
cd "L:/project(AI review helper)" && python web_app.py
```

The quiz is available at **http://127.0.0.1:5050**.

Tell the user:
- The URL to open
- How many questions
- What topics are covered
- To answer ALL questions for a complete diagnostic

### Step 6: Report & Diagnosis

After the user finishes the quiz, the web UI shows:
- Overall score and time
- Per-topic accuracy, speed ratio, and mastery level
- Specific weak subtopics
- Personalized study recommendations
- Link to full HTML report

The HTML report is saved in `L:\project(AI review helper)\reports\`.

Tell the user:
- Their weakest topics
- What specifically to review
- Whether to retake or move on

## Quiz Engine Details

The web quiz provides:
- Real-time per-question timer (green/yellow/red based on expected time)
- Hint system (+30s penalty)
- Skip option
- Keyboard shortcuts (a/b/c/d for MC, Enter for fill-in)
- Immediate correct/wrong feedback
- Progress bar
- Results dashboard with topic mastery breakdown

Server runs on port 5050. If port is in use, kill the old process first.

## Question Bank Persistence

The question bank at `L:\project(AI review helper)\question_bank.json` is overwritten each time new questions are generated. The quiz engine reads from this file live — no restart needed if the server is already running (the server loads questions at session start).

## Example

User: "Here's my Math 10 Unit 5 notes on Quadratic Functions, quiz me"

1. Read the notes (from Obsidian or user-provided material)
2. Generate 12-16 questions covering: solving, discriminant, vertex form, graphs, applications
3. Write to question_bank.json
4. Start server if needed
5. Tell user: "Quiz ready at http://127.0.0.1:5050 — 16 questions on Quadratic Functions"
6. After completion, review the report and give targeted advice
