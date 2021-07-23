import nox


@nox.session(python=["3.6", "3.7", "3.8", "3.9", "3.10"], reuse_venv=True)
def tests(session: nox.Session) -> None:
    session.run("pip", "install", "-r", "requirements-test.txt")
    session.run("pytest", "-s", "--verbose")
