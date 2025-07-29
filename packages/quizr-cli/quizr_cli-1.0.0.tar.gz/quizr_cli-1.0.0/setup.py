"""
Setup script for QUIZR
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="quizr-cli",
    version="1.0.0",
    author="QUIZR Team",
    author_email="sipistab@gmail.com",
    description="A command-line quiz tool with spaced repetition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sipistab/QUIZR",
    project_urls={
        "Bug Tracker": "https://github.com/sipistab/QUIZR/issues",
        "Documentation": "https://github.com/sipistab/QUIZR#readme",
    },
    packages=find_packages(exclude=["tests*", "docs*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Education",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Education",
        "Topic :: Education :: Testing",
    ],
    keywords="quiz, learning, spaced-repetition, education, cli",
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "quizr=quizr.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "quizr": ["py.typed"],
    },
) 