from setuptools import setup, find_packages

with open("PYPI_README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tavix",
    version="0.1.1",
    author="Atharva Dethe",
    author_email="atharvadethe2004@gmail.com",
    description="An AI-powered shell assistant using Google Gemini API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Atharvadethe/Tavix",
    packages=find_packages(),
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "tavix=tavix.main:app",
            "tx=tavix.main:app",
        ],
    },
    keywords="ai, shell, cli, gemini, assistant, automation",
    project_urls={
        "Bug Reports": "https://github.com/Atharvadethe/Tavix/issues",
        "Source": "https://github.com/Atharvadethe/Tavix",
        "Documentation": "https://github.com/Atharvadethe/Tavix#readme",
    },
) 