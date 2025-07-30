from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="jict-dict",
    version="1.0.0",
    packages=find_packages(),
    long_description=README,
    long_description_content_type="text/markdown",
    # ... your other metadata ...
)
