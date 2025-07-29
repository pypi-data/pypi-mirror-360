from setuptools import setup, find_packages

# Read the version from _version.py
with open("src/debase/_version.py") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split('"')[1]
            break

# Read the content of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="debase",
    version=version,
    author="DEBase Team",
    author_email="ylong@caltech.edu",
    description="Enzyme lineage analysis and sequence extraction package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YuemingLong/DEBase",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.0.0",
        "PyMuPDF>=1.18.0",
        "numpy>=1.19.0",
        "google-generativeai>=0.3.0",
        "biopython>=1.78",
        "requests>=2.25.0",
        "httpx>=0.24.0",
        "tqdm>=4.60.0",
        "openpyxl>=3.0.0",
        "PyPDF2>=2.0.0",
        "Pillow>=8.0.0",
        "networkx>=2.5"
    ],
    extras_require={
        "rdkit": ["rdkit>=2020.03.1"]
    },
    entry_points={
        "console_scripts": [
            "debase=debase.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
)