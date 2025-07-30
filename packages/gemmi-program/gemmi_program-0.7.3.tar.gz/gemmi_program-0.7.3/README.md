## gemmi executable in a wheel

Here we provide the command-line program
[gemmi](https://gemmi.readthedocs.io/en/latest/utils.html)
in [wheels](https://github.com/project-gemmi/gemmi_program_wheel).

It is, in PyPI, distributed separately from the Python extension module
[gemmi](https://pypi.org/project/gemmi/),
because, unlike the module, it does not depend on Python version.

### notes for myself -- how to make wheels after gemmi release

* update:
  * `GIT_TAG` in CMakeLists.txt
  * `version` in pyproject.toml
  * scikit-build-core version in pyproject.toml (optional)
  * cibuildwheel version in .github/workflows/wheels.yml (optional)
* test locally with `pip wheel .`
* make source distribution of this repo: `python -m build --sdist`
* git push changes to build wheels in [GitHub Actions][1]
* download the wheels, check them, upload sdist and wheels to PyPI:

      twine upload dist/gemmi_program-$VERSION.tar.gz
      twine upload wheels/gemmi_program-$VERSION-*.whl

[1]: https://github.com/project-gemmi/gemmi_program_wheel/actions
