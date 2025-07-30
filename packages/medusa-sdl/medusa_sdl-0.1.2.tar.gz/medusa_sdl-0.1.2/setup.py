from setuptools import setup

if __name__ == "__main__":
    setup(
        # This is necessary due to a potential issue with setuptools 69.x
        # not correctly reading python-requires from pyproject.toml.
        # The standard location is in pyproject.toml under [project].
        # python_requires='>=3.6',
    )