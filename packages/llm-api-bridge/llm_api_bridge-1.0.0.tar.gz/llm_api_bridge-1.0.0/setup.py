# setup.py
from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="llm-api-bridge",  # This will be the pip install name
    version="1.0.0",
    author="Hunzala Rasheed",  # Replace with your name
    author_email="hunzalarasheed14@gmail.com",  # Replace with your email
    description="A unified interface for querying multiple LLM providers via REST APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hunzala-Rasheed1/llmconnect",  # Replace with your repo URL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "python-dotenv>=0.19.0",
        ],
    },
    keywords="llm, ai, openai, claude, gemini, api, chatbot, nlp",
    project_urls={
        "Bug Reports": "https://github.com/Hunzala-Rasheed1/llmconnect/issues",
        "Source": "https://github.com/yourusername/llmconnect",
        "Documentation": "https://github.com/Hunzala-Rasheed1/llmconnect#readme",
    },
)