"""PHARVO Selenium smoke-test runner.

Discovers every ``test_*.py`` module in this directory, runs each test case
against Brave, and writes a human-readable PASS/FAIL report to a text file.

Usage:
    python run_all_tests.py
"""
import datetime
import glob
import importlib.util
import io
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


def load_test_suites():
    """Import every test_*.py file in the tests directory."""
    suites = []
    for path in sorted(glob.glob(os.path.join(TEST_DIR, "test_*.py"))):
        module_name = os.path.splitext(os.path.basename(path))[0]
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suites.append(module)
    return suites


class Reporter(unittest.TextTestResult):
    """Captures per-test PASS/FAIL outcomes for the final report."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = []  # list of (test_id, outcome, message)

    def _record(self, test, outcome, err=None):
        message = ""
        if err:
            exc_type, exc_value, _tb = err
            message = f"{exc_type.__name__}: {exc_value}"
        self.results.append((str(test), outcome, message))

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, "FAIL", err)

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, "ERROR", err)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, "SKIP")


def generate_report(results, summary):
    """Build a markdown-style PASS/FAIL report string."""
    lines = []
    lines.append("=" * 70)
    lines.append("PHARVO FRONTEND — SELENIUM TEST REPORT")
    lines.append(f"Generated: {datetime.datetime.now().isoformat(timespec='seconds')}")
    lines.append("Browser: Brave (Chromium) via Selenium")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"{'Feature':<34}{'Test case':<0}")
    lines.append("-" * 70)

    header = None
    for test_id, outcome, message in results:
        # test_id is like "module.Class.test_case"
        parts = test_id.split(".")
        module, cls, case = parts[0], parts[1], parts[2] if len(parts) > 2 else ""
        if cls != header:
            header = cls
            lines.append("")
            lines.append(f"## {module}.{cls}")
        status = "PASS" if outcome == "PASS" else "FAIL" if outcome == "FAIL" else outcome
        lines.append(f"  [{'PASS' if status=='PASS' else 'FAIL'}] {case}")
        if message:
            lines.append(f"        -> {message}")

    lines.append("")
    lines.append("=" * 70)
    lines.append("SUMMARY")
    lines.append("-" * 70)
    lines.append(f"  Total  : {summary['total']}")
    lines.append(f"  Passed : {summary['passed']}")
    lines.append(f"  Failed : {summary['failed']}")
    lines.append(f"  Errors : {summary['errors']}")
    lines.append(f"  Skipped: {summary['skipped']}")
    lines.append("")
    lines.append("OVERALL: " + ("ALL TESTS PASSED" if summary["failed"] == 0 and summary["errors"] == 0 else "SOME TESTS FAILED"))
    lines.append("=" * 70)
    return "\n".join(lines)


def main():
    suites = load_test_suites()
    loader = unittest.TestLoader()
    all_tests = unittest.TestSuite()
    for module in suites:
        for test_class in vars(module).values():
            if isinstance(test_class, type) and issubclass(test_class, unittest.TestCase):
                all_tests.addTests(loader.loadTestsFromTestCase(test_class))

    stream = io.StringIO()
    runner = unittest.TextTestRunner(
        stream=stream, verbosity=2, resultclass=Reporter
    )
    result = runner.run(all_tests)

    results = result.results
    summary = {
        "total": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
        "failed": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
    }

    report = generate_report(results, summary)

    # Show concise live output and full report.
    print("=" * 30)
    print(stream.getvalue())
    report_path = os.path.join(TEST_DIR, "TEST_REPORT.txt")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(report)
    print("\n" + report)
    print(f"\nReport written to: {report_path}")

    return 1 if (summary["failed"] or summary["errors"]) else 0


if __name__ == "__main__":
    sys.exit(main())