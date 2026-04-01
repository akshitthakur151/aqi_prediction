"""
setup.py
Setup configuration for AQI Prediction package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aqi-predictor",
    version="1.0.0",
    author="Your Name",
    description="Advanced Air Quality Index Prediction System for India",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aqi-prediction",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.23.0",
        "pandas>=1.5.0",
        "scikit-learn>=1.2.0",
        "xgboost>=2.0.0",
        "fastapi>=0.100.0",
        "streamlit>=1.28.0",
    ],
    entry_points={
        "console_scripts": [
            "aqi-predictor=main:main",
        ],
    },
)
