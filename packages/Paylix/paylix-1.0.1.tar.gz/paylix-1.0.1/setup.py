from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="Paylix",  # ✅ This is your PyPI name (shown on pip)
    version="1.0.1",
    author="Paylix",  # Optional: show who built it
    author_email="you@example.com",  # Optional: your contact
    description="Official Paylix Python SDK",
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type='text/markdown',
    url='https://github.com/Dboosts2/paylix-python-sdk',  # ✅ Update this to your repo
    packages=find_packages(),  # will include paylix/ and paylix/resources/*
    install_requires=[
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.7',
)
