#!/usr/bin/env python3
"""
PA1 - Student Grade Management System - Batch Grader
INSTRUCTOR-ONLY. Never distributed to students.

Usage:
    python3 batch_grader.py <submissions_dir>

<submissions_dir> must contain one ZIP file per student
(e.g. Firstname_Lastname.zip), each containing gradebook.py and README.txt
(files may be nested in subfolders; no other files permitted).

Run this script from the assignment directory (the one containing
autograder.py, gradebook_interface.py).
"""

import sys, os, shutil, zipfile, subprocess, re, glob, datetime

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
REQUIRED_FILES = ["gradebook.py", "README.txt"]
AUTOGRADER_SCRIPT = "A1_autograder.py"
RESULTS_DIR = "GRADING_RESULTS"
TOTAL_POSSIBLE = 80
AUTOGRADER_TIMEOUT_SECONDS = 30

SCORE_RE = re.compile(r"Final Score:\s*(\d+)\s*/\s*(\d+)")


def check_environment():
    major, minor = sys.version_info[0], sys.version_info[1]
    if (major, minor) < (3, 13):
        print(f"[WARN] Running on Python {major}.{minor}; "
              f"the shipped autograder requires 3.13+ for students, but "
              f"batch grading itself works fine on any Python 3.9+.")
        print()


def reset_working_directory():
    """Guaranteed clean slate before/after every submission."""
    for f in REQUIRED_FILES:
        if os.path.exists(f):
            os.remove(f)
    for extra in ("__pycache__",):
        shutil.rmtree(extra, ignore_errors=True)


def find_required_files(extract_dir):
    """Locate each required filename anywhere in the extracted tree.
    Returns (ok: bool, paths: dict, issues: list[str])."""
    all_files = []
    for root, _, files in os.walk(extract_dir):
        if "__MACOSX" in root:
            continue
        for f in files:
            all_files.append(os.path.join(root, f))

    issues = []
    paths = {}
    for name in REQUIRED_FILES:
        matches = [p for p in all_files if os.path.basename(p) == name]
        if len(matches) == 0:
            issues.append(f"Missing required file: {name}")
        elif len(matches) > 1:
            issues.append(f"Ambiguous: multiple copies of {name} found")
        else:
            paths[name] = matches[0]

    if len(all_files) > len(REQUIRED_FILES):
        issues.append("Extra file(s) present beyond the required set")

    return (len(issues) == 0), paths, issues, all_files


def check_readme_sections(readme_path):
    try:
        content = open(readme_path, encoding="utf-8", errors="replace").read().upper()
    except Exception:
        return ["[Could not read README.txt]"]
    flags = []
    for section in ("TEAM DETAILS", "AI DISCLOSURE", "AI CRITIQUE"):
        if section not in content:
            flags.append(f"[Missing: {section}]")
    return flags


def grade_one(zip_path, results_dir):
    student_name = os.path.splitext(os.path.basename(zip_path))[0]
    grade_file = os.path.join(results_dir, f"{student_name}_grade.txt")
    log_lines = []

    def log(msg=""):
        print(msg)
        log_lines.append(msg)

    log("=" * 42)
    log(f"  {ASSIGNMENT_NAME} \u2014 Grading Report")
    log(f"  Student : {student_name}")
    log(f"  ZIP     : {os.path.basename(zip_path)}")
    log(f"  Graded  : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 42)
    log()

    reset_working_directory()
    extract_dir = f"_extract_{student_name}"
    shutil.rmtree(extract_dir, ignore_errors=True)
    os.makedirs(extract_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(extract_dir)
    except Exception:
        log("  Error: Could not extract ZIP file.")
        open(grade_file, "w", encoding="utf-8").write("\n".join(log_lines))
        shutil.rmtree(extract_dir, ignore_errors=True)
        reset_working_directory()
        return student_name, "EXTRACTION_FAILED", None

    ok, paths, issues, all_files = find_required_files(extract_dir)
    if not ok:
        log("  [FAIL] Error:")
        log("          ZIP contents invalid.")
        log("          Required (exact case-sensitive filenames anywhere in the ZIP):")
        for name in REQUIRED_FILES:
            log(f"              - {name}")
        log("          No other files are permitted anywhere in the ZIP.")
        for issue in issues:
            log(f"              - {issue}")
        log("          Files found in this ZIP:")
        for f in all_files:
            log(f"              - {os.path.relpath(f, extract_dir)}")
        open(grade_file, "w", encoding="utf-8").write("\n".join(log_lines))
        shutil.rmtree(extract_dir, ignore_errors=True)
        reset_working_directory()
        return student_name, "INVALID_ZIP_STRUCTURE", None

    flags = check_readme_sections(paths["README.txt"])
    if flags:
        msg = f"  Warning: README section(s) not found: {' '.join(flags)}"
        log(msg)

    for name in REQUIRED_FILES:
        shutil.copy(paths[name], f"./{name}")

    try:
        result = subprocess.run(
            [sys.executable, AUTOGRADER_SCRIPT],
            capture_output=True, text=True, timeout=AUTOGRADER_TIMEOUT_SECONDS,
            encoding="utf-8", errors="replace",
        )
        output = (result.stdout or "") + (result.stderr or "")
        for line in output.splitlines():
            if re.match(r"^\s+\S.*:\s*(PASSED|PARTIAL|FAILED)", line) or "Final Score" in line or line.startswith("---"):
                print(line)
        log_lines.append(output)

        match = SCORE_RE.search(output)
        if match:
            score = int(match.group(1))
            status = f"{score} / {TOTAL_POSSIBLE}"
            shutil.rmtree(extract_dir, ignore_errors=True)
            reset_working_directory()
            open(grade_file, "w", encoding="utf-8").write("\n".join(log_lines))
            return student_name, status, score
        else:
            shutil.rmtree(extract_dir, ignore_errors=True)
            reset_working_directory()
            open(grade_file, "w", encoding="utf-8").write("\n".join(log_lines))
            return student_name, "SCORE_PARSE_ERROR", 0
    except subprocess.TimeoutExpired:
        log("  Error: Autograder timed out.")
        shutil.rmtree(extract_dir, ignore_errors=True)
        reset_working_directory()
        open(grade_file, "w", encoding="utf-8").write("\n".join(log_lines))
        return student_name, "TIMEOUT", 0
    except Exception as e:
        log(f"  Error: Autograder failed ({e}).")
        shutil.rmtree(extract_dir, ignore_errors=True)
        reset_working_directory()
        open(grade_file, "w", encoding="utf-8").write("\n".join(log_lines))
        return student_name, "AUTOGRADER_FAILED", 0


def main():
    check_environment()
    if len(sys.argv) != 2:
        print("[WARN] Usage: python3 batch_grader.py <submissions_dir>")
        sys.exit(1)

    submissions_dir = sys.argv[1]
    if not os.path.isdir(submissions_dir):
        print(f"[WARN] ERROR: {submissions_dir} is not a directory")
        sys.exit(1)
    if not os.path.isfile(AUTOGRADER_SCRIPT):
        print(f"[WARN] ERROR: {AUTOGRADER_SCRIPT} not found in current directory. "
              f"Run this from the assignment directory.")
        sys.exit(1)

    print("=" * 42)
    print(f"  Batch Grader \u2014 {ASSIGNMENT_NAME}")
    print(f"  {datetime.datetime.now()}")
    print("=" * 42)
    print()

    zip_files = sorted(glob.glob(os.path.join(submissions_dir, "*.zip")))
    if not zip_files:
        print("No ZIP files found in submissions directory.")
        sys.exit(1)
    print(f"Found {len(zip_files)} submission(s).")
    print()

    shutil.rmtree(RESULTS_DIR, ignore_errors=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    summary_path = os.path.join(RESULTS_DIR, "GRADE_SUMMARY.txt")

    total, graded, failed, perfect = 0, 0, 0, 0
    all_scores = []
    summary_lines = [
        f"{ASSIGNMENT_NAME} \u2014 Grading Summary",
        f"Generated: {datetime.datetime.now()}",
        "=" * 65,
    ]

    for i, zip_path in enumerate(zip_files, 1):
        total += 1
        print("=" * 42)
        student_name, status, score = grade_one(zip_path, RESULTS_DIR)
        summary_lines.append(f"{i}. {student_name} : {status}")
        summary_lines.append("")
        if score is not None:
            graded += 1
            all_scores.append(score)
            if score == TOTAL_POSSIBLE:
                perfect += 1
        else:
            failed += 1
        print()

    summary_lines += [
        "=" * 65,
        "  STATISTICS",
        "=" * 65,
        f"Total processed : {total}",
        f"Successfully graded : {graded}",
        f"Failed          : {failed}",
        f"Perfect scores  : {perfect}",
        "",
        f"Results directory : {RESULTS_DIR}/",
    ]

    if all_scores:
        avg_score = sum(all_scores) / len(all_scores)
        summary_lines += [
            f"Score statistics \u2014 AUTOGRADER PORTION ONLY (out of {TOTAL_POSSIBLE} pts):",
            f"  Average : {avg_score:.1f} / {TOTAL_POSSIBLE}",
            f"  Highest : {max(all_scores)} / {TOTAL_POSSIBLE}",
            f"  Lowest  : {min(all_scores)} / {TOTAL_POSSIBLE}",
        ]

    open(summary_path, "w", encoding="utf-8").write("\n".join(summary_lines))

    print("=" * 42)
    print("  Batch Grading Complete")
    print(f"  Total   : {total}")
    print(f"  Graded  : {graded}")
    print(f"  Failed  : {failed}")
    print(f"  Perfect : {perfect}")
    print()
    print(f"  Summary : {summary_path}")
    print("=" * 42)


if __name__ == "__main__":
    main()
