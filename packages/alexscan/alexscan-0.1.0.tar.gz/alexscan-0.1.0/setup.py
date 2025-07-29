from pathlib import Path

from setuptools import find_packages, setup


def read_requirements(file_path: str) -> list:
    """Read requirements from a file."""
    requirements_path = Path(__file__).parent / file_path
    if requirements_path.exists():
        return requirements_path.read_text().strip().split("\n")
    return []


def read_version() -> str:
    """Read version from VERSION file."""
    version_path = Path(__file__).parent / "alexscan" / "VERSION"
    return version_path.read_text().strip()


def read_readme() -> str:
    """Read long description from README."""
    readme_path = Path(__file__).parent / "README.md"
    return readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""


# Read dependencies from requirements files
install_requires = read_requirements("requirements.txt")
dev_requires = read_requirements("requirements-dev.txt")

setup(
    name="alexscan",
    version=read_version(),
    description="A production-grade domain analysis CLI tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Alex Evan",
    author_email="",
    url="https://github.com/alexevan/alexscan",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "alexscan": ["VERSION"],
    },
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
    },
    entry_points={
        "console_scripts": [
            "alexscan=alexscan.cli:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
)
