from config import (
    GRADE_A,
    GRADE_A_THRESHOLD,
    GRADE_B,
    GRADE_B_THRESHOLD,
    GRADE_C,
    GRADE_C_THRESHOLD,
    GRADE_D,
    GRADE_D_THRESHOLD,
    GRADE_F,
)


def calculate_grade(score: float) -> str:
    if score >= GRADE_A_THRESHOLD:
        return GRADE_A
    elif score >= GRADE_B_THRESHOLD:
        return GRADE_B
    elif score >= GRADE_C_THRESHOLD:
        return GRADE_C
    elif score >= GRADE_D_THRESHOLD:
        return GRADE_D
    return GRADE_F


def calculate_statistics(students: list) -> dict:
    if not students:
        return {
            "total_students": 0,
            "average_score": 0.0,
            "highest_score": 0.0,
            "lowest_score": 0.0,
        }

    scores = [s["score"] for s in students]
    total_students = len(scores)
    average_score = round(sum(scores) / total_students, 1)
    highest_score = max(scores)
    lowest_score = min(scores)

    return {
        "total_students": total_students,
        "average_score": average_score,
        "highest_score": highest_score,
        "lowest_score": lowest_score,
    }