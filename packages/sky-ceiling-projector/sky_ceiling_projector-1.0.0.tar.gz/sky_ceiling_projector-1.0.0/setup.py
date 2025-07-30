#!/usr/bin/env python3

from setuptools import setup, find_packages
import pathlib

# Read the README file
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="sky-ceiling-projector",
    version="1.0.0",
    author="Sky Projector Team",
    author_email="your-email@example.com",
    description="A realistic sky ceiling projector with weather effects, celestial objects, and enhanced starfield",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sky-ceiling-projector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics :: Presentation",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pygame>=2.0.0",
        "requests>=2.25.0",
        "numpy>=1.20.0",
        "pytz>=2021.1",
    ],
    extras_require={
        "enhanced": [
            "geopy>=2.0.0",
            "timezonefinder>=6.0.0",
        ],
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "sky-projector=sky_projector.main:main",
            "sky-ceiling-projector=sky_projector.main:main",
        ],
    },
    keywords="astronomy projector ceiling sky weather stars moon planets pygame raspberry-pi",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/sky-ceiling-projector/issues",
        "Source": "https://github.com/yourusername/sky-ceiling-projector",
        "Documentation": "https://github.com/yourusername/sky-ceiling-projector#readme",
    },
    include_package_data=True,
    zip_safe=False,
)