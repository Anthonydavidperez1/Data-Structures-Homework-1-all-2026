#!/usr/bin/env python3
"""
PA1 - Student Grade Management System - Autograder
Run: python3 autograder.py
(gradebook.py and gradebook_interface.py must be in the same directory.)
"""

import sys, os, importlib, traceback

# --- UTF-8 output safety net -----------------------------------------------
# Windows consoles sometimes default to a legacy codepage (e.g. cp1252) that
# cannot encode the checkmark/warning symbols used below, which previously
# caused an unhandled UnicodeEncodeError instead of a clean message. This
# guarantees UTF-8 output regardless of the host console's configuration.
if sys.stdout.encoding is None or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding is None or sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


ASSIGNMENT_NAME = "Student Grade Management System"
TOTAL_POINTS = 80
STUDENT_MODULE = "gradebook"

IS_TTY = sys.stdout.isatty()
RED = "\033[0;31m" if IS_TTY else ""
GREEN = "\033[0;32m" if IS_TTY else ""
YELLOW = "\033[1;33m" if IS_TTY else ""
NC = "\033[0m" if IS_TTY else ""

def perr(msg): print(f"{RED}[FAIL] {msg}{NC}")
def pok(msg):  print(f"{GREEN}[PASS] {msg}{NC}")
def pwarn(msg):print(f"{YELLOW}[WARN] {msg}{NC}")


def check_environment():
    major, minor = sys.version_info[0], sys.version_info[1]
    if (major, minor) < (3, 13):
        print("Testing script compatibility on this computer...")
        perr(f"Python version: FAILED (found {major}.{minor}, need 3.13+)")
        print()
        print("[WARN] Please install Python 3.13+ and re-run. See the \"Python Setup\"")
        print("   module in Canvas for platform-specific instructions.")
        sys.exit(1)


def check_readme():
    # Informational only -- never affects the autograder score.
    if not os.path.isfile("README.txt"):
        pwarn("README.txt not found in this directory.")
        print("      It will not affect this autograder score,")
        print("      but it IS required in your submission ZIP and")
        print("      is worth 10 points, graded manually.")
        print("      See the assignment specification.")
        print()
        return
    content = open("README.txt", encoding="utf-8", errors="replace").read().upper()
    flags = []
    for section in ("TEAM DETAILS", "AI DISCLOSURE", "AI CRITIQUE"):
        if section not in content:
            flags.append(f"[Missing: {section}]")
    if flags:
        pwarn(f"README.txt section(s) not found: {' '.join(flags)}")
        print("    This will not affect this autograder score, but these sections are")
        print("    worth 10 points, graded manually. Fix this before submitting.")
        print()


def check_student_file():
    if not os.path.isfile("gradebook.py"):
        perr("gradebook.py not found. Ensure your file is named exactly: gradebook.py")
        print(f"Final Score: 0 / {TOTAL_POINTS}")
        sys.exit(1)
    pok("gradebook.py found")


def load_student_class():
    try:
        if STUDENT_MODULE in sys.modules:
            del sys.modules[STUDENT_MODULE]
        mod = importlib.import_module(STUDENT_MODULE)
        return mod.GradeBook
    except Exception:
        perr("gradebook.py failed to import.")
        print()
        traceback.print_exc()
        print()
        print(f"Final Score: 0 / {TOTAL_POINTS}")
        sys.exit(1)


# ------------------------------------------------------------------------
# Test definitions. Each test is a list of ordered steps:
#   ("setup", method_name, args, expected_setup_return)  -- uses student's
#       own method (dependency-aware isolation: if the dependency itself
#       is broken, the DEPENDENT test's steps below simply won't reach a
#       correct starting state, which is scored as a failure of the
#       dependent test only -- the setup step is not separately scored).
#   ("check", method_name, args, expected_return)        -- this call's
#       return value IS what's scored against expected_return.
# ------------------------------------------------------------------------

TESTS = {
    "add_student": {
        "weight": 13,
        "cases": [
            ("basic add", [("check", "add_student", ("s1", "Alice", "CS"), True)]),
            ("duplicate id rejected", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("check", "add_student", ("s1", "Bob", "IT"), False),
            ]),
            ("empty name rejected", [("check", "add_student", ("s2", "", "CS"), False)]),
            ("whitespace-only major rejected", [("check", "add_student", ("s3", "Carl", "   "), False)]),
        ],
    },
    "add_grade": {
        "weight": 13,
        "cases": [
            ("basic add", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("check", "add_grade", ("s1", "COP3538", 95.0), True),
            ]),
            ("nonexistent student rejected", [("check", "add_grade", ("ghost", "COP3538", 90.0), False)]),
            ("score above 100 rejected", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("check", "add_grade", ("s1", "COP3538", 101.0), False),
            ]),
            ("score below 0 rejected", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("check", "add_grade", ("s1", "COP3538", -1.0), False),
            ]),
            ("empty course_code rejected", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("check", "add_grade", ("s1", "", 90.0), False),
            ]),
            ("boundary score 0.0 accepted", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("check", "add_grade", ("s1", "COP3538", 0.0), True),
            ]),
            ("boundary score 100.0 accepted", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("check", "add_grade", ("s1", "COP3538", 100.0), True),
            ]),
        ],
    },
    "remove_student": {
        "weight": 13,
        "cases": [
            ("remove existing", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("check", "remove_student", ("s1",), True),
            ]),
            ("remove nonexistent", [("check", "remove_student", ("ghost",), False)]),
            ("removed student's grades gone (via GPA=None after re-check)", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("setup", "add_grade", ("s1", "COP3538", 95.0), True),
                ("setup", "remove_student", ("s1",), True),
                ("check", "calculate_gpa", ("s1",), None),
            ]),
        ],
    },
    "calculate_gpa": {
        "weight": 13,
        "cases": [
            ("nonexistent student", [("check", "calculate_gpa", ("ghost",), None)]),
            ("no grades yet", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("check", "calculate_gpa", ("s1",), None),
            ]),
            ("single A", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("setup", "add_grade", ("s1", "COP3538", 95.0), True),
                ("check", "calculate_gpa", ("s1",), 4.0),
            ]),
            ("mixed courses average", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("setup", "add_grade", ("s1", "COP3538", 95.0), True),   # 4.0
                ("setup", "add_grade", ("s1", "MAC2311", 82.0), True),  # 3.0
                ("check", "calculate_gpa", ("s1",), 3.5),
            ]),
            ("boundary 89.99 is a B not an A", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("setup", "add_grade", ("s1", "COP3538", 89.99), True),
                ("check", "calculate_gpa", ("s1",), 3.0),
            ]),
            ("boundary exactly 90.0 is an A", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("setup", "add_grade", ("s1", "COP3538", 90.0), True),
                ("check", "calculate_gpa", ("s1",), 4.0),
            ]),
            ("boundary exactly 80.0 is a B", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("setup", "add_grade", ("s1", "COP3538", 80.0), True),
                ("check", "calculate_gpa", ("s1",), 3.0),
            ]),
        ],
    },
    "get_class_average": {
        "weight": 14,
        "cases": [
            ("no one enrolled", [("check", "get_class_average", ("GHOST101",), None)]),
            ("single student", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("setup", "add_grade", ("s1", "COP3538", 90.0), True),
                ("check", "get_class_average", ("COP3538",), 90.0),
            ]),
            ("two students averaged", [
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("setup", "add_grade", ("s1", "COP3538", 90.0), True),
                ("setup", "add_student", ("s2", "Bob", "IT"), True),
                ("setup", "add_grade", ("s2", "COP3538", 80.0), True),
                ("check", "get_class_average", ("COP3538",), 85.0),
            ]),
        ],
    },
    "get_honor_roll": {
        "weight": 14,
        "cases": [
            ("empty gradebook", [("check", "get_honor_roll", (), [])]),
            ("one qualifies one does not", [
                ("setup", "add_student", ("s2", "Bob", "IT"), True),
                ("setup", "add_grade", ("s2", "COP3538", 70.0), True),  # 2.0 GPA
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("setup", "add_grade", ("s1", "COP3538", 95.0), True),  # 4.0 GPA
                ("check", "get_honor_roll", (), ["s1"]),
            ]),
            ("sorted ascending, custom threshold", [
                ("setup", "add_student", ("s2", "Bob", "IT"), True),
                ("setup", "add_grade", ("s2", "COP3538", 85.0), True),  # 3.0
                ("setup", "add_student", ("s1", "Alice", "CS"), True),
                ("setup", "add_grade", ("s1", "COP3538", 82.0), True),  # 3.0
                ("check", "get_honor_roll", (2.5,), ["s1", "s2"]),
            ]),
            ("no-grades student never qualifies", [
                ("setup", "add_student", ("s3", "Carl", "CS"), True),
                ("check", "get_honor_roll", (0.0,), []),
            ]),
        ],
    },
}


def run_case(GradeBookClass, steps):
    """Fresh instance per case. Returns (passed: bool, detail: str|None)."""
    gb = GradeBookClass()
    for step in steps:
        kind, method_name, args, expected = step
        method = getattr(gb, method_name, None)
        if method is None:
            return False, f"method '{method_name}' not found on your GradeBook class"
        try:
            actual = method(*args)
        except Exception as e:
            return False, f"raised {type(e).__name__}: {e}"
        if kind == "check":
            if actual != expected:
                return False, f"expected {expected!r}, got {actual!r}"
    return True, None


def round_points(correct, total, max_pts):
    # Mirrors the bash autograder's integer arithmetic exactly:
    # (2*correct*max_pts + total) // (2*total) -- true floor division,
    # NOT Python's round() (which uses round-half-to-even and would
    # incorrectly inflate a full-credit case, e.g. 13/13 -> 14).
    if total == 0:
        return 0
    return (2 * correct * max_pts + total) // (2 * total)


import signal

PER_CASE_TIMEOUT_SECONDS = 5


class _CaseTimeout(Exception):
    pass


def _alarm_handler(signum, frame):
    raise _CaseTimeout()


def run_case_tracked(GradeBookClass, steps):
    """Like run_case, but also returns the raw 'check'-step actual value(s),
    so the caller can detect an unimplemented stub that accidentally
    matches a None-expected case (e.g. `pass` returning None coincides
    with a legitimate 'no grades yet -> None' expectation).

    Wrapped in a per-case SIGALRM timeout so a student infinite loop
    (e.g. `while True: pass` inside a method) fails only that one case
    instead of hanging the entire autograder run. SIGALRM is available
    on Linux/macOS/WSL (all platforms this course's Canvas setup guides
    target); on a platform without it, this degrades to "no timeout"
    rather than crashing the autograder.
    """
    gb = GradeBookClass()
    actual_values = []
    has_alarm = hasattr(signal, "SIGALRM")
    if has_alarm:
        old_handler = signal.signal(signal.SIGALRM, _alarm_handler)
        signal.alarm(PER_CASE_TIMEOUT_SECONDS)
    try:
        for step in steps:
            kind, method_name, args, expected = step
            method = getattr(gb, method_name, None)
            if method is None:
                return False, f"method '{method_name}' not found on your GradeBook class", actual_values
            try:
                actual = method(*args)
            except _CaseTimeout:
                return False, f"timed out (exceeded {PER_CASE_TIMEOUT_SECONDS}s -- check for an infinite loop)", actual_values
            except Exception as e:
                return False, f"raised {type(e).__name__}: {e}", actual_values
            if kind == "check":
                actual_values.append(actual)
                if actual != expected:
                    return False, f"expected {expected!r}, got {actual!r}", actual_values
        return True, None, actual_values
    finally:
        if has_alarm:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)


def run_tests(GradeBookClass):
    test_points = []
    for method_name, spec in TESTS.items():
        weight = spec["weight"]
        cases = spec["cases"]
        correct = 0
        failures = []
        all_actuals = []
        for case_name, steps in cases:
            passed, detail, actuals = run_case_tracked(GradeBookClass, steps)
            all_actuals.extend(actuals)
            if passed:
                correct += 1
            else:
                failures.append((case_name, detail))
        # Stub-collision guard: if this method NEVER returned anything but
        # None across every case (i.e. it looks unimplemented, matching
        # the `pass` skeleton's default return), any passing cases were
        # accidental None==None matches, not real credit -- zero them out.
        if all_actuals and all(v is None for v in all_actuals) and correct > 0:
            correct = 0
            failures = [(name, "method appears unimplemented (always returns None)") for name, _ in cases]
        pts = round_points(correct, len(cases), weight)
        test_points.append(pts)
        if correct == len(cases):
            print(f"    {method_name:<20s}: PASSED  [{pts}/{weight} pts]  ({correct}/{len(cases)} cases)")
        elif correct == 0:
            print(f"    {method_name:<20s}: FAILED  [{pts}/{weight} pts]  (0/{len(cases)} cases)")
        else:
            print(f"    {method_name:<20s}: PARTIAL [{pts}/{weight} pts]  ({correct}/{len(cases)} cases)")
        for case_name, detail in failures[:3]:
            print(f"        - {case_name}: {detail}")
        if len(failures) > 3:
            print(f"        - ... and {len(failures) - 3} more failing case(s)")
    print()
    return test_points


def final_grade(test_points):
    total = sum(test_points)
    print("------------------------------")
    print(f"Final Score: {total} / {TOTAL_POINTS}")
    print("------------------------------")
    return total


def main():
    check_environment()
    print(f"Assignment : {ASSIGNMENT_NAME}")
    import datetime
    print(f"Submitted  : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    check_readme()
    check_student_file()
    GradeBookClass = load_student_class()
    total_cases = sum(len(spec["cases"]) for spec in TESTS.values())
    worst_case_seconds = total_cases * PER_CASE_TIMEOUT_SECONDS
    worst_case_minutes = (worst_case_seconds + 59) // 60
    print(f"Grading... Please wait (up to {worst_case_minutes} min in case of timeout or infinite loop).")
    print()
    print("RUNNING TEST CASES")
    test_points = run_tests(GradeBookClass)
    final_grade(test_points)


if __name__ == "__main__":
    main()
