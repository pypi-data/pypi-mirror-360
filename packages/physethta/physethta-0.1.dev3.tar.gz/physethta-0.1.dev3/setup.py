from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="physethta",
    use_scm_version=True,
    setup_requires=["setuptools-scm"],
    description="Assignment tool for physics TAs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sebastian Huber",
    author_email="huberse@phys.ethz.ch",
    url="https://gitlab.phys.ethz.ch/sebastian.huber/physethta",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas",
        "pyyaml",
        "openpyxl"
    ],
    entry_points={
        "console_scripts": [
            "run_assignment = physethta.run_assignment:main"
        ]
    },
    python_requires=">=3.8"
)