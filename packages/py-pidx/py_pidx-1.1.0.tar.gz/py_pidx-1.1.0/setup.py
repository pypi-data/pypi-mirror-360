import setuptools
from pathlib import Path

root = Path(__file__).resolve().parent
readme_path = root.parent / "README.md"

with open(readme_path, "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="py_pidx",
    version="1.0.0",
    author="Mehrab Mahdian",
    author_email="memahdian@outlook.com",
    description="py_pidx: A Python package for PID control.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mehrabmahdian/py_pidx",
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
