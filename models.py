"""Data models for the AI Review Helper learning diagnosis system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class Subject(str, Enum):
    MATH = "math"
    PHYSICS = "physics"
    ENGLISH = "english"

    @classmethod
    def from_str(cls, value: str) -> "Subject":
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Unknown subject: {value}. Supported: {[s.value for s in cls]}")


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class Question:
    question_id: str
    subject: str
    topic: str
    subtopic: str
    question_type: str  # multiple_choice, fill_blank, short_answer
    question_text: str
    options: List[str]
    correct_answer: str
    expected_time_seconds: int
    difficulty: str
    hint: str = ""


@dataclass
class QuizSession:
    session_id: str
    student_name: str
    subject: str
    topics: List[str]
    created_at: str
    completed_at: Optional[str] = None
    total_questions: int = 0
    correct_count: int = 0
    total_time_seconds: float = 0.0


@dataclass
class Answer:
    answer_id: str
    session_id: str
    question_id: str
    question_text: str
    topic: str
    subtopic: str
    student_answer: str
    correct_answer: str
    is_correct: bool
    actual_time_seconds: float
    expected_time_seconds: int
    recorded_at: str


@dataclass
class TopicAnalysis:
    topic: str
    total_questions: int
    correct_count: int
    accuracy: float
    avg_actual_time: float
    avg_expected_time: float
    speed_ratio: float  # < 1 = faster than expected, > 1 = slower
    streak_data: List[bool]  # consecutive results
    weak_subtopics: List[str]
    recommendation: str
    mastery_level: str  # mastered, proficient, developing, needs_review


@dataclass
class SessionReport:
    session_id: str
    student_name: str
    subject: str
    created_at: str
    total_score: float
    total_time: float
    overall_accuracy: float
    topic_analyses: List[TopicAnalysis]
    top_weaknesses: List[str]
    study_recommendations: List[str]
