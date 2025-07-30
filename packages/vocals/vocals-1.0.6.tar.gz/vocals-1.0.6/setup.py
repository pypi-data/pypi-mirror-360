#!/usr/bin/env python3
"""
Setup script for Vocals SDK Python package
"""

from setuptools import setup, find_packages

# Read requirements from requirements.txt
try:
    with open("requirements.txt", "r") as f:
        requirements = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]
except FileNotFoundError:
    # Fallback requirements if requirements.txt is not available (e.g., during build)
    requirements = [
        "aiohttp>=3.8.0",
        "websockets>=11.0.0",
        "sounddevice>=0.4.6",
        "numpy>=1.21.0",
        "PyJWT>=2.8.0",
        "python-dotenv>=1.0.0",
        "typing-extensions>=4.0.0",
        "pyaudio>=0.2.11",
        "soundfile>=0.12.1",
        "click>=8.0.0",
        "psutil>=5.9.0",
        "matplotlib>=3.5.0",
    ]

# Read README for long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="vocals",
    version="1.0.6",
    description="A Python SDK for voice processing and real-time audio communication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Vocals Team",
    author_email="support@vocals.dev",
    url="https://github.com/hairetsucodes/vocals-sdk-python",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "vocals=vocals.cli:cli",
            "vocals-demo=vocals.cli:demo",
            "vocals-setup=vocals.cli:setup",
            "vocals-test=vocals.cli:test",
            "vocals-devices=vocals.cli:devices",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    keywords="vocals, audio, speech, websocket, real-time, voice processing",
    project_urls={
        "Bug Reports": "https://github.com/vocals/vocals-sdk-python/issues",
        "Source": "https://github.com/vocals/vocals-sdk-python",
        "Documentation": "https://docs.vocals.dev",
    },
)
