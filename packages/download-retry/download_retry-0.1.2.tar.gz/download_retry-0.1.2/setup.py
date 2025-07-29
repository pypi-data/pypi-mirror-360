"""Module setup"""
from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="download-retry",
    version="0.1.2",
    py_modules=["download_retry"],
    install_requires=["requests"],
    entry_points={
        'console_scripts': [
            'download-retry = download_retry:main',
        ],
    },
    author="Gil Weisbord",
    description="Retry downloading a binary file from a URL with timeout and optional SSL check.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)
