import nox


@nox.session(python=["3.6", "3.7", "3.8", "3.9", "3.10"], reuse_venv=True)
def tests(session: nox.Session) -> None:
    session.run("pip", "install", "-r", "requirements-test.txt")
    session.run("pytest", "-s", "--verbose", "--log-level=INFO")


@nox.session(reuse_venv=True)
def check_formatting(session: nox.Session) -> None:
    with open("./requirements-dev.txt", mode="r", encoding="utf-8") as f:
        for l in f:
            if l.startswith("black"):
                black_version = l.split("==")[1]
                break

    session.run("pip", "install", f"black=={black_version}")
    session.run("black", ".", "--check")
