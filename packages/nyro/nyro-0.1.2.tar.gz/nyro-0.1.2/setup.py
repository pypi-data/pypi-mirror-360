"""
Nyro Package Setup
🧵 Synth: Terminal orchestration for package installation

Consolidates 13+ bash scripts into unified Python package with:
- Multi-database Upstash Redis support
- Interactive CLI replacing all bash menus
- Musical ledger integration
- Four-perspective Assembly testing
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
README_PATH = Path(__file__).parent / "README.md"
long_description = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""

# Read requirements
requirements = [
    "requests>=2.25.0",
    "pathlib>=1.0.0",
    "dataclasses>=0.6;python_version<'3.7'",
]

# Development requirements  
dev_requirements = [
    "pytest>=6.0.0",
    "pytest-cov>=2.10.0",
    "black>=21.0.0",
    "flake8>=3.8.0",
    "mypy>=0.800",
]

# Musical requirements (optional)
musical_requirements = [
    "musicpy>=6.0.0",
    "mido>=1.2.0",
]

setup(
    name="nyro",
    version="0.1.2",
    author="Jerry ⚡ G.Music Assembly Team",
    author_email="gerico@jgwill.com",
    description="♠️🌿🎸🧵 Unified Redis Operations Package - Consolidating 13+ bash scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gerico1007/nyro",
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
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "musical": musical_requirements,
        "all": dev_requirements + musical_requirements,
    },
    entry_points={
        "console_scripts": [
            "nyro=nyro.cli.main:main",
            "nyro-interactive=nyro.cli.interactive:main", 
            "nyro-test=testing.test_framework:run_assembly_tests",
        ],
    },
    include_package_data=True,
    package_data={
        "nyro": ["*.md", "*.abc"],
        "testing": ["*.md"],
    },
    project_urls={
        "Bug Reports": "https://github.com/gerico1007/nyro/issues",
        "Source": "https://github.com/gerico1007/nyro",
        "Documentation": "https://github.com/gerico1007/nyro/wiki",
        "G.Music Assembly": "https://github.com/gerico1007/nyro/tree/main/assembly",
    },
    keywords="redis upstash database cli music assembly consolidation",
    zip_safe=False,
)