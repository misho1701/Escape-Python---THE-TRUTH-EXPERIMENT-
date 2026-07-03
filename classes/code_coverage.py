import unittest
import coverage
import sys


def run_tests_with_coverage():
    cov = coverage.Coverage(source=["."])
    cov.start()

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    cov.stop()
    cov.save()

    print("\n================ COVERAGE REPORT ================\n")
    cov.report(show_missing=True)

    cov.html_report(directory="htmlcov")
    print("\nHTML report generated in: htmlcov/index.html")

    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    run_tests_with_coverage()