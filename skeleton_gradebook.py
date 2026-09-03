"""
PA1 - Student Grade Management System
Skeleton file. Rename this file to gradebook.py before implementing.

Implement every method of GradeBook below. Each method has a brief summary
docstring here to remind you what it does at a glance -- but gradebook_interface.py
is still the authoritative spec: read it thoroughly before starting, since it has
the exact validation rules, edge cases, and return conditions for every method.
Do not change any method's name or parameters.
"""

from gradebook_interface import GradeBookInterface


class GradeBook(GradeBookInterface):

    def __init__(self):
        self.students = {}

    def add_student(self, student_id: str, name: str, major: str) -> bool:
        if student_id in self.students:
            return False

        if not isinstance(name, str) or not name.strip():
            return False

        if not isinstance(major, str) or not major.strip():
            return False

        self.students[student_id] = {
            "name": name,
            "major": major,
            "grades": {}
        }

        return True

    def add_grade(self, student_id: str, course_code: str, score: float) -> bool:
        if student_id not in self.students:
            return False

        if not isinstance(course_code, str) or not course_code.strip():
            return False

        if isinstance(score, bool) or not isinstance(score, (int, float)):
            return False

        if score < 0.0 or score > 100.0:
            return False

        course_code = course_code.strip()

        self.students[student_id]["grades"][course_code] = score

        return True

    def remove_student(self, student_id: str) -> bool:
        if student_id not in self.students:
            return False

        del self.students[student_id]

        return True

    def calculate_gpa(self, student_id: str):
        """Convert the student's recorded scores to grade points and
        average them. See gradebook_interface.py for the exact
        score-to-grade-point cutoffs and rounding rule.
        """
        pass

    def get_class_average(self, course_code: str):
        """Average the scores of every student with a grade in
        course_code. See gradebook_interface.py for the exact
        rounding rule and what to return when no student qualifies.
        """
        pass

    def get_honor_roll(self, min_gpa: float = 3.5) -> list:
        """Return the student_ids of everyone whose GPA meets min_gpa.
        See gradebook_interface.py for the exact sort order and how
        students with no grades are handled.
        """
        pass