"""Multi-dimensional weak point analysis engine."""

from typing import Dict, List, Tuple

from models import TopicAnalysis


def analyze_session(answers: List[dict]) -> List[TopicAnalysis]:
    """Run full multi-dimensional analysis on a completed quiz session."""
    by_topic: Dict[str, List[dict]] = {}
    for a in answers:
        topic = a["topic"]
        if topic not in by_topic:
            by_topic[topic] = []
        by_topic[topic].append(a)

    results = []
    for topic, items in by_topic.items():
        results.append(_analyze_topic(topic, items))

    return sorted(results, key=lambda t: t.accuracy)


def _analyze_topic(topic: str, items: List[dict]) -> TopicAnalysis:
    total = len(items)
    correct = sum(1 for a in items if a["is_correct"])
    accuracy = correct / total if total > 0 else 0.0

    avg_actual = sum(a["actual_time_seconds"] for a in items) / total if total > 0 else 0.0
    avg_expected = sum(a["expected_time_seconds"] for a in items) / total if total > 0 else 0.0
    speed_ratio = avg_actual / avg_expected if avg_expected > 0 else 1.0

    # Streak analysis
    streak_data = [bool(a["is_correct"]) for a in items]

    # Identify weak subtopics
    by_subtopic: Dict[str, List[bool]] = {}
    for a in items:
        st = a["subtopic"]
        if st not in by_subtopic:
            by_subtopic[st] = []
        by_subtopic[st].append(a["is_correct"])
    weak_subtopics = [
        st for st, results in by_subtopic.items()
        if sum(results) / len(results) < 0.6
    ]

    # Mastery level
    mastery = _determine_mastery(accuracy, speed_ratio, streak_data)

    # Generate recommendation
    recommendation = _generate_recommendation(topic, accuracy, speed_ratio, streak_data, weak_subtopics, items)

    return TopicAnalysis(
        topic=topic,
        total_questions=total,
        correct_count=correct,
        accuracy=round(accuracy * 100, 1),
        avg_actual_time=round(avg_actual, 1),
        avg_expected_time=round(avg_expected, 1),
        speed_ratio=round(speed_ratio, 2),
        streak_data=streak_data,
        weak_subtopics=weak_subtopics,
        recommendation=recommendation,
        mastery_level=mastery,
    )


def _determine_mastery(accuracy: float, speed_ratio: float, streaks: List[bool]) -> str:
    """Determine mastery level from multi-dimensional signals."""
    score = 0

    # Accuracy component (0-40)
    score += accuracy * 40

    # Speed component (0-30)
    if speed_ratio <= 0.7:
        score += 30  # Fast and accurate = good
    elif speed_ratio <= 0.9:
        score += 25
    elif speed_ratio <= 1.1:
        score += 20  # On pace
    elif speed_ratio <= 1.5:
        score += 12  # A bit slow
    else:
        score += 5   # Very slow

    # Streak component (0-30)
    if len(streaks) >= 3:
        # Check for streaks of 3+ correct
        max_streak = 0
        current = 0
        for s in streaks:
            if s:
                current += 1
                max_streak = max(max_streak, current)
            else:
                current = 0
        if max_streak >= 4:
            score += 25
        elif max_streak >= 3:
            score += 20
        elif max_streak >= 2:
            score += 10
        else:
            score += 3
    else:
        score += 15  # Not enough data

    if score >= 85:
        return "mastered"
    elif score >= 65:
        return "proficient"
    elif score >= 40:
        return "developing"
    else:
        return "needs_review"


def _generate_recommendation(
    topic: str, accuracy: float, speed_ratio: float,
    streaks: List[bool], weak_subtopics: List[str], items: List[dict]
) -> str:
    """Generate personalized study recommendation."""
    parts = []

    if accuracy < 0.5:
        parts.append(f"URGENT: {topic} accuracy is only {accuracy*100:.0f}%. "
                     f"Review core concepts before attempting more problems.")
    elif accuracy < 0.7:
        parts.append(f"{topic} needs improvement ({accuracy*100:.0f}%). "
                     f"Focus on understanding why wrong answers were chosen.")
    elif accuracy < 0.85:
        parts.append(f"{topic} is decent but not yet solid ({accuracy*100:.0f}%). "
                     f"Target the specific subtopics you got wrong.")
    else:
        parts.append(f"{topic} is strong ({accuracy*100:.0f}%). "
                     f"Challenge yourself with harder problems.")

    if speed_ratio > 1.5:
        parts.append(f"You are significantly slower than expected ({speed_ratio:.1f}x). "
                     f"Practice timed drills to build speed.")
    elif speed_ratio > 1.2:
        parts.append(f"You are somewhat slower than expected ({speed_ratio:.1f}x). "
                     f"Aim to increase pace without sacrificing accuracy.")
    elif speed_ratio < 0.6:
        parts.append(f"You are very fast ({speed_ratio:.1f}x). "
                     f"Double-check that speed is not causing careless errors.")
    else:
        parts.append(f"Your pace is appropriate ({speed_ratio:.1f}x expected).")

    if weak_subtopics:
        parts.append(f"Weak areas: {', '.join(weak_subtopics)}. "
                     f"Do targeted practice on these topics.")

    consecutive_wrong = 0
    for s in reversed(streaks):
        if not s:
            consecutive_wrong += 1
        else:
            break
    if consecutive_wrong >= 2:
        parts.append(f"You ended with {consecutive_wrong} consecutive wrong answers. "
                     f"Take a break and come back fresh.")

    return " ".join(parts)


def generate_overall_recommendations(
    topic_analyses: List[TopicAnalysis],
    total_questions: int, correct_count: int, total_time: float
) -> List[str]:
    """Generate high-level study recommendations based on full session analysis."""
    recommendations = []
    accuracy = correct_count / total_questions if total_questions > 0 else 0

    # Sort by weakness
    weakest = [t for t in topic_analyses if t.mastery_level in ("needs_review", "developing")]
    strongest = [t for t in topic_analyses if t.mastery_level == "mastered"]

    if weakest:
        names = ", ".join(t.topic for t in weakest)
        recommendations.append(f"Priority 1: Review {names} — these are your weakest areas.")

    if accuracy < 0.6:
        recommendations.append("Overall accuracy is below 60%. Consider retaking this quiz after targeted review.")
    elif accuracy >= 0.9:
        recommendations.append("Excellent overall performance! Move on to harder material or the next unit.")

    # Check for time issues
    avg_speed = sum(t.speed_ratio for t in topic_analyses) / len(topic_analyses) if topic_analyses else 1.0
    if avg_speed > 1.5:
        recommendations.append(f"Time management is a concern — average speed is {avg_speed:.1f}x expected. Practice under timed conditions.")
    elif avg_speed > 1.2:
        recommendations.append(f"Slightly slow pace ({avg_speed:.1f}x). Try timed practice sets of 5 questions each.")

    # Streak-based advice
    for t in topic_analyses:
        if len(t.streak_data) >= 3:
            # Check for alternating pattern (inconsistent)
            alt = sum(1 for i in range(len(t.streak_data) - 1)
                      if t.streak_data[i] != t.streak_data[i + 1])
            if alt >= len(t.streak_data) - 1 and t.accuracy < 80:
                recommendations.append(
                    f"{t.topic}: Your answers alternate between right and wrong — "
                    f"this suggests guessing. Slow down and solve each problem fully."
                )
                break

    return recommendations
