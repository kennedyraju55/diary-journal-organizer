"""Setup script for Diary Journal Organizer."""
from setuptools import setup, find_packages

setup(
    name="diary-journal-organizer",
    version="1.0.0",
    description="Private diary with AI-powered insights, mood analysis, and theme discovery.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Diary Journal Team",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.0.0",
        "click>=8.1.0",
        "pyyaml>=6.0",
        "streamlit>=1.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "diary-organizer=diary_organizer.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
