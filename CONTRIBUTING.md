# Contributing

Thanks for considering contributing to analytix! Before you begin, take a minute to read the below information.

## Expectations

- All code should follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) standards.
- All code should support the versions analytix already supported. The only exception is when contributing something related to pandas, which may not support the latest version of Python.
- Commit messages should be clear and easy to understand.
- Issue and PR descriptions should be much the same.
- New features and fixes should be properly tested before committing.
- All PRs should correspond to at least one issue.

## First time contributing?

No worries, we all start somewhere. It may be best off to start with an already existing issue, or by trying to fix a simple oversight before moving onto more complicated things. Kent Dodds [made a guide](https://egghead.io/courses/how-to-contribute-to-an-open-source-project-on-github) outlining how to contribute to open source projects.

## Making your contribution

If you are making a very small change (one or two lines), it would be better to simply supply the code in the issue itself. You will be co-authored in the relevant commit. Otherwise:

1. Fork the repository.
2. Clone your fork.
3. Run `pip install -e ".[dev]"` to install the cloned library.
4. Make your changes/additions.
5. Run `black .` in the project root to format the code properly.
6. Run `nox` to run the tests. If they all pass, advance to step 7, otherwise, go back to step 4.
7. Create a PR with your changes, making sure to provide the issue number(s) it relates to.

After you've submitted your PR, feedback will be given on it. It may be approved straight away, or changes may be requested. Your PR may not be immediately merged when it's ready, but so long as it's marked as approved, you don't need to do anything.
