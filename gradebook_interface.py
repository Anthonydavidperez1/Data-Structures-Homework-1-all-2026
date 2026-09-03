"""
PA1 - Student Grade Management System
Abstract interface. DO NOT MODIFY THIS FILE.

Your GradeBook class (in gradebook.py) must inherit from GradeBookInterface
and implement every method below exactly as documented.
"""

from abc import ABC, abstractmethod


class GradeBookError(Exception):
    """Base exception for GradeBook errors (available for your own use if needed)."""
    pass


class GradeBookInterface(ABC):

    @abstractmethod
    def add_student(self, student_id: str, name: str, major: str) -> bool:
        """
        Add a new student to the gradebook.

        Returns True and stores the student if all of the following hold:
          - student_id is not already present in the gradebook
          - name is a non-empty string (after stripping whitespace)
          - major is a non-empty string (after stripping whitespace)

        Returns False (and makes no change) if any condition above fails.
        """
        raise NotImplementedError

    @abstractmethod
    def add_grade(self, student_id: str, course_code: str, score: float) -> bool:
        """
        Record one course score for an existing student.

        Returns True and stores the grade if all of the following hold:
          - student_id exists in the gradebook
          - course_code is a non-empty string (after stripping whitespace)
          - score is a number with 0.0 <= score <= 100.0

        Returns False (and makes no change) if any condition above fails.
        A student may have at most one score per course_code; adding a
        grade for a course_code the student already has REPLACES the old
        score and still returns True.
        """
        raise NotImplementedError

    @abstractmethod
    def remove_student(self, student_id: str) -> bool:
        """
        Remove a student and all of their recorded grades.

        Returns True if the student existed and was removed.
        Returns False if the student_id was not found.
        """
        raise NotImplementedError

    @abstractmethod
    def calculate_gpa(self, student_id: str):
        """
        Calculate a student's GPA on a 4.0 scale from their recorded scores.

        Per-course score -> grade point conversion (use these exact cutoffs):
            90.0 <= score <= 100.0  -> 4.0
            80.0 <= score < 90.0    -> 3.0
            70.0 <= score < 80.0    -> 2.0
            60.0 <= score < 70.0    -> 1.0
            0.0  <= score < 60.0    -> 0.0

        GPA = average of grade points across all of the student's recorded
        courses, rounded to 2 decimal places using standard round-half-up
        rounding (i.e. Python's round()).

        Returns the GPA (float) if the student exists AND has at least one
        recorded grade.
        Returns None if the student does not exist, or exists but has no
        recorded grades.
        """
        raise NotImplementedError

    @abstractmethod
    def get_class_average(self, course_code: str):
        """
        Calculate the average score across every student who has a
        recorded grade for course_code.

        Returns the average (float, rounded to 2 decimal places) if at
        least one student has a grade in that course.
        Returns None if no student has a recorded grade for that
        course_code (including courses that don't exist at all).
        """
        raise NotImplementedError

    @abstractmethod
    def get_honor_roll(self, min_gpa: float = 3.5) -> list:
        """
        Return the student_ids of every student whose GPA (as defined by
        calculate_gpa) is >= min_gpa.

        A student with no recorded grades (GPA is None) is never on the
        honor roll, regardless of min_gpa.

        Returns a list of student_id strings sorted in ascending
        alphabetical order. Returns an empty list if no student qualifies.
        """
        raise NotImplementedError
