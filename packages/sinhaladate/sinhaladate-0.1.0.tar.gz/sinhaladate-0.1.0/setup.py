from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sinhaladate",
    version="0.1.0",
    author="Ravindu Pabasara Karunarathna",
    author_email="karurpabe@gmail.com",
    description="A Python library for parsing and formatting Sinhala dates and times",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RavinduPabasara/sinhaladate",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="sinhala, date, time, parsing, formatting, sri lanka, natural language",
    project_urls={
        "Bug Reports": "https://github.com/RavinduPabasara/sinhaladate/issues",
        "Source": "https://github.com/RavinduPabasara/sinhaladate",
        "Documentation": "https://github.com/RavinduPabasara/sinhaladate#readme",
    },
    include_package_data=False,
) 