#!/usr/bin/env python3
"""
Setup script for OpenTestability package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text().splitlines() 
        if line.strip() and not line.startswith('#')
    ]
else:
    requirements = [
        'networkx>=3.0',
        'pyverilog>=1.3.0',
        'matplotlib>=3.0',
        'pygraphviz>=1.10',
        'ply>=3.11'
    ]

setup(
    name="opentestability",
    version="1.0.0",
    author="OpenTestability Contributors",
    author_email="ranaumarnadeem632@gmail.com",
    description="Comprehensive Gate-Level Testability Analysis Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ranaumarnadeem/OpenTestability",
    
    # Package configuration
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    
    # Dependencies
    install_requires=requirements,
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Entry points for CLI
    entry_points={
        "console_scripts": [
            "opentestability=opentestability.cli:main",
        ],
    },
    
    # Package data
    package_data={
        "opentestability": ["*.py"],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    
    # Keywords
    keywords="testability, SCOAP, DFT, VLSI, EDA, digital-design, fault-simulation",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/ranaumarnadeem/OpenTestability/issues",
        "Source": "https://github.com/ranaumarnadeem/OpenTestability",
        "Documentation": "https://github.com/ranaumarnadeem/OpenTestability/blob/main/README.md",
    },
)