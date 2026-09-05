#!/usr/bin/env python3
"""
PA1 - Student Grade Management System
gradebook.py - Student implementation

Implements every method of GradeBookInterface (see gradebook_interface.py
for the authoritative spec on each method's exact behavior, including all
validation rules and edge cases). This file does not modify the interface.
"""

from gradebook_interface import GradeBookInterface, GradeBookError


# --- Grade point conversion table -------------------------------------------
# Ordered high-to-low so the first matching (low, high) bound wins.
# high is exclusive except for the top bracket, which is inclusive of 100.0.
GRADE_POINT_TABLE = [
    (90.0, 100.0, 4.0),
    (80.0, 90.0, 3.0),
    (70.0, 80.0, 2.0),
    (60.0, 70.0, 1.0),
    (0.0, 60.0, 0.0),
]


def _score_to_grade_points(score: float) -> float:
    """Convert a single course score to grade points using the exact
    cutoffs defined in gradebook_interface.py's calculate_gpa docstring."""
    for low, high, points in GRADE_POINT_TABLE:
        in_top_bracket = high == 100.0 and low <= score <= high
        in_lower_bracket = high != 100.0 and low <= score < high
        if in_top_bracket or in_lower_bracket:
            return points
    # Should be unreachable if add_grade validation is correct, but guard
    # against a stray out-of-range value ever reaching here.
    raise GradeBookError(f"Score {score} is outside the valid 0-100 range.")


class GradeBook(GradeBookInterface):
    """Stores students and their course grades and answers questions
    about them (GPA, class averages, honor roll)."""

    def __init__(self):
        # student_id -> {"name": str, "major": str, "grades": {course_code: score}}
        self._students = {}

    # -------------------------------------------------------------------
    # 1. add_student
    # -------------------------------------------------------------------
    def add_student(self, student_id: str, name: str, major: str) -> bool:
        if student_id in self._students:
            return False

        name_clean = name.strip() if isinstance(name, str) else ""
        major_clean = major.strip() if isinstance(major, str) else ""
        if not name_clean or not major_clean:
            return False

        self._students[student_id] = {
            "name": name_clean,
            "major": major_clean,
            "grades": {},
        }
        return True

    # -------------------------------------------------------------------
    # 2. add_grade
    # -------------------------------------------------------------------
    def add_grade(self, student_id: str, course_code: str, score: float) -> bool:
        if student_id not in self._students:
            return False

        course_clean = course_code.strip() if isinstance(course_code, str) else ""
        if not course_clean:
            return False

        # Reject non-numeric scores (e.g. None, strings) before range-checking.
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            return False
        if not (0.0 <= score <= 100.0):
            return False

        # Replaces any existing score for this course_code.
        self._students[student_id]["grades"][course_clean] = float(score)
        return True

    # -------------------------------------------------------------------
    # 3. remove_student
    # -------------------------------------------------------------------
    def remove_student(self, student_id: str) -> bool:
        if student_id not in self._students:
            return False
        del self._students[student_id]
        return True

    # -------------------------------------------------------------------
    # 4. calculate_gpa
    # -------------------------------------------------------------------
    def calculate_gpa(self, student_id: str):
        if student_id not in self._students:
            return None

        grades = self._students[student_id]["grades"]
        if not grades:
            return None

        points = [_score_to_grade_points(score) for score in grades.values()]
        gpa = sum(points) / len(points)
        return round(gpa, 2)

    # -------------------------------------------------------------------
    # 5. get_class_average
    # -------------------------------------------------------------------
    def get_class_average(self, course_code: str):
        scores = [
            record["grades"][course_code]
            for record in self._students.values()
            if course_code in record["grades"]
        ]
        if not scores:
            return None
        return round(sum(scores) / len(scores), 2)

    # -------------------------------------------------------------------
    # 6. get_honor_roll
    # -------------------------------------------------------------------
    def get_honor_roll(self, min_gpa: float = 3.5) -> list:
        qualifying = []
        for student_id in self._students:
            gpa = self.calculate_gpa(student_id)
            if gpa is not None and gpa >= min_gpa:
                qualifying.append(student_id)
        return sorted(qualifying)
