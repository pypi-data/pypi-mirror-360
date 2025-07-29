import os.path
import pathlib
import re

from setuptools import setup

PROJECT_NAME = "stream_llm_parser"
HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()


def get_property(prop):
    result = re.search(
        r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop),
        open(os.path.join(PROJECT_NAME, "__init__.py")).read(),
    )
    assert result, f"Property {prop} not found in {PROJECT_NAME}/__init__.py"
    return result.group(1)


setup(
    name="stream_llm_parser",
    version=get_property("__version__"),
    description="stream_llm_parser is a Python library for parsing and processing streaming data with special token handling.",
    long_description=README,
    long_description_content_type="text/markdown",
    url=get_property("__url__"),
    author=get_property("__author__"),
    author_email=get_property("__author_email__"),
    license=get_property("__license__"),
    packages=["stream_llm_parser"],
)
