from setuptools import setup, find_packages
import os

# Read version from package __init__.py
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), "src", "aiwand", "__init__.py")
    with open(init_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    raise RuntimeError("Version not found")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aiwand",
    version=get_version(),
    author="Aman Kumar",
    author_email="2000.aman.sinha@gmail.com",
    description="A simple AI toolkit for text processing using OpenAI and Gemini APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/onlyoneaman/aiwand",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "aiwand=aiwand.cli:main",
        ],
    },
) 