from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="pulse-ui",
    version="1.0.0",
    author="tikisan",
    author_email="s2501082@sendai-nct.jp",
    description="A modern Python GUI library with React-like components and utility-first styling.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tikipiya/PulseUI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
    ],
    python_requires=">=3.10",
    install_requires=[
        "PyOpenGL>=3.1.0",
        "PyOpenGL-accelerate>=3.1.0",
        "pygame>=2.1.0",
        "numpy>=1.21.0",
        "Pillow>=9.0.0",
        "moderngl>=5.6.0",
        "pyrr>=0.10.0",
        "glfw>=2.5.0",
        "freetype-py>=2.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pulse-ui=pulse_ui.cli:main",
        ],
    },
)