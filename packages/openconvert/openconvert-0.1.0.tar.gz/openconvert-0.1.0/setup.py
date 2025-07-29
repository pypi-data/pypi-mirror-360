from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openconvert",
    version="0.1.0",
    author="OpenConvert Team",
    author_email="info@openconvert.org",
    description="A versatile file and data conversion library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openconvert/openconvert",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pillow",  # For image conversions
        "reportlab",  # For PDF creation
        "python-docx",  # For DOCX handling
        "PyPDF2",  # For PDF handling
        "pandas",  # For data conversions
        "pyyaml",  # For YAML handling
        "dicttoxml",  # For XML conversions
        "xmltodict",  # For XML parsing
        "markdown",  # For Markdown handling
        "beautifulsoup4",  # For HTML parsing
        "html2text",  # For HTML to Markdown conversion
    ],
    extras_require={
        "image": [
            "cairosvg",  # For SVG conversions
        ],
        "audio": [
            "pydub",  # For audio conversions
            "SpeechRecognition",  # For speech-to-text
        ],
        "video": [
            "moviepy",  # For video processing
        ],
        "document": [
            "pdf2image",  # For PDF to image conversion
        ],
        "archive": [
            "py7zr",  # For 7z handling
            "rarfile",  # For RAR handling
        ],
        "model": [
            "trimesh",  # For 3D model handling
            "numpy",  # Required by trimesh
            "scipy",  # Required for 3D transformations
        ],
        "all": [
            "cairosvg",
            "pydub",
            "SpeechRecognition",
            "moviepy",
            "pdf2image",
            "py7zr",
            "rarfile",
            "trimesh",
            "numpy",
            "scipy",
        ],
    },
    entry_points={
        "console_scripts": [
            "openconvert=openconvert.cli:main",
        ],
    },
) 