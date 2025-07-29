from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python_eicar",
    version="0.1.1",
    description="EICAR test string utility for AV detection testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/khalidwalidalamri/python-eicar",
    license="MIT",
    packages= find_packages(),
    install_requires=[],
    entry_points= {
        "console_scripts": [
            "eicar-print = python_eicar:eicar_print",
        ],
    },


)