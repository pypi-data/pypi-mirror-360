from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="artbot_Philippe_Noa",
    version="0.2.4",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "requests",
        "beautifulsoup4",
        "pillow",
    ],
    entry_points={
        "console_scripts": [
            "artbot=artbot.api:endpoint",
        ],
    },
    author="GambeyNoa/MathieuPhilippe",
    description="Un convertisseur d'images vers ASCII à partir d'URLs Unsplash",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.8',
)
