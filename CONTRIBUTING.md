# Contributing

Thanks for considering contributing to analytix! Before you begin, take a minute to read the below information.

## Expectations

* All code should follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) standards
* All code should support the Python versions analytix already supported, unless there's a good reason otherwise (such as contributing a feature that requires pandas)
* Commit messages should be clear and easy to understand
* Issue and PR descriptions should be much the same
* New features and fixes should be properly tested before committing

And of course, always follow the [code of conduct](https://github.com/parafoxia/analytix/blob/main/CODE_OF_CONDUCT.md).

## First time contributing?

No worries, we all start somewhere. It may be best off to start with an already existing issue, or by trying to fix a simple oversight before moving onto more complicated things. Kent Dodds [made a guide](https://egghead.io/courses/how-to-contribute-to-an-open-source-project-on-github) outlining how to contribute to open source projects.

## Making your contribution

If you are making a very small change (one or two lines), it would be better to simply supply the code in the issue itself. You will be co-authored in the relevant commit. Otherwise:

1. Fork the repository
2. Clone your fork
3. Run `pip install -r requirements/dev.txt` to install the cloned library and all development dependencies
4. Make your changes/additions
5. Run `nox` to run the checks and tests. If they all pass, advance to step 6, otherwise, go back to step 4
6. Create a PR with your changes, making sure to provide the issue number(s) it relates to

After you've submitted your PR, feedback will be given on it. It may be approved straight away, or changes may be requested. Your PR may not be immediately merged when it's ready, but so long as it's marked as approved, you don't need to do anything.
