#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pdf-ocr",
    version="2.0.0",
    author="Seyed Mahdi Vakhshoori",
    author_email="seyedmahdivakhshoori@gmail.com",
    description="نرم‌افزار هوشمند استخراج اطلاعات از فایل‌های PDF اظهارنامه",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seyedmahdivakhshoori/pdf-ocr",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pdf-ocr=pdf_ocr:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.pdf", "fonts/*.ttf"],
    },
    keywords="pdf, ocr, openai, chatgpt, persian, farsi, invoice, extraction",
    project_urls={
        "Source": "https://github.com/seyedmahdivakhshoori/pdf-ocr",
        "Documentation": "https://github.com/seyedmahdivakhshoori/pdf-ocr#readme",
    },
) 