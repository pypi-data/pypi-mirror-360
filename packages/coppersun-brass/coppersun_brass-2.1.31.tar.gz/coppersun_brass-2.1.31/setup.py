"""Setup configuration for Copper Sun Brass."""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="coppersun-brass",
    version="2.1.31",
    description="Development Intelligence for AI Agents - Copper Sun Product Line",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Copper Sun Team",
    author_email="brass@coppersun.com",
    url="https://github.com/coppersun/brass",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies (minimal)
        "click>=8.0",
        "pydantic>=2.0",
        "aiofiles>=0.8", 
        "watchdog>=3.0.0",  # Match requirements.txt
        "jsonschema>=4.0",
        "networkx>=3.0",
        "pyyaml>=6.0",
        "pyperclip>=1.8",  # For Claude Code integration copy-paste
        "requests>=2.28",  # For LemonSqueezy API calls
        "urllib3>=1.26,<2",  # Avoid LibreSSL warnings on macOS (urllib3 v2.x issue)
        "anthropic>=0.21.3",  # CRITICAL: Missing dependency for CLI integration
        "python-dotenv>=1.0.0",  # For environment configuration
        
        # Phase 3 Content Safety Dependencies (Professional Libraries)
        # DataFog and alt-profanity-check removed - replaced with Blood Oath compliant regex detector
        
        # Optional but recommended
        "apscheduler>=3.10",  # For scheduling
        "rich>=13.0",  # For better CLI output
        
        # BLOOD OATH DISABLED: Can add heavy dependencies for now
    ],
    extras_require={
        "ml": [
            # BLOOD OATH DISABLED: Can add external ML dependencies for now
        ],
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21",
            "pytest-cov>=4.0",
            "black>=23.0",
            "mypy>=1.5",
            "ruff>=0.1",
        ],
        "all": [
            # 🩸 BLOOD OATH: Pure Python ML - NO external ML dependencies
            "apscheduler>=3.10",
            "rich>=13.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "brass=coppersun_brass.cli.brass_cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="code-analysis ai ml devops automation copper-sun brass",
)