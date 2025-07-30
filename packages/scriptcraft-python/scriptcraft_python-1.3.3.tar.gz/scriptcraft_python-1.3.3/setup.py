"""
Setup script for ScriptCraft Python implementation.
"""

from setuptools import setup, find_packages
from pathlib import Path
import sys
import os

# Add the package directory to the path so we can import version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scriptcraft'))
from _version import __version__, __author__

# Read README
readme_path = Path(__file__).parent.parent.parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "ScriptCraft - Data processing and quality control workspace for research data"

setup(
    name="scriptcraft-python",
    version=__version__,
    description="Data processing and quality control tools for research workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=__author__,
    author_email="scriptcraft@example.com",
    url="https://github.com/mcusac/ScriptCraft-Workspace",
    project_urls={
        "Bug Reports": "https://github.com/mcusac/ScriptCraft-Workspace/issues",
        "Source": "https://github.com/mcusac/ScriptCraft-Workspace",
        "Documentation": "https://github.com/mcusac/ScriptCraft-Workspace/wiki",
    },
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "pyyaml>=5.4.1",
        "pandas>=1.3.0",
        "numpy>=1.20.0", 
        "python-dateutil>=2.8.2",
        "openpyxl>=3.0.0",
        "python-docx>=0.8.11",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        # Web automation tools (RHQ Form Autofiller)
        "web": ["selenium>=4.0.0"],
        
        # Development tools
        "dev": [
            "pytest>=6.2.5", 
            "pytest-cov>=2.12.1",
            "black>=21.12b0",
            "mypy>=0.910",
            "flake8>=3.9.0",
        ],
        
        # Full installation with all optional dependencies
        "all": [
            "selenium>=4.0.0",
            "pytest>=6.2.5", 
            "pytest-cov>=2.12.1",
        ],
    },
    entry_points={
        "console_scripts": [
            # Main CLI entry point
            "scriptcraft=scriptcraft.common.cli:main",
            
            # Individual tool shortcuts for power users
            "rhq-autofiller=scriptcraft.tools.rhq_form_autofiller:main",
            "data-comparer=scriptcraft.tools.data_content_comparer:main", 
            "auto-labeler=scriptcraft.tools.automated_labeler:main",
        ],
    },
    include_package_data=True,
    package_data={
        "scriptcraft": [
            "*.yaml", "*.yml", "*.json",
            "templates/**/*",
            "tests/**/*",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="data-processing, quality-control, research, validation, automation",
    zip_safe=False,
) 