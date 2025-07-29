"""Nox information."""

import nox

PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session):
    """Run the test suite."""
    # Install all test dependencies
    session.install(".[test]")
    # Run pytest against the tests directory
    session.run("pytest", "tests/", "--cov=lod_unit")
