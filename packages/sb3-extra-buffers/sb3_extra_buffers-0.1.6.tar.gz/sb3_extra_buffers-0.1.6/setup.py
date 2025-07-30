import os
from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

with open(os.path.join("sb3_extra_buffers", "version.txt")) as file_handler:
    __version__ = file_handler.read().strip()

setup(
    name="sb3_extra_buffers",
    version=__version__,
    author="Hugo (Jin Huang)",
    author_email="SushiNinja123@outlook.com",
    url="https://github.com/Trenza1ore/sb3-extra-buffers",
    description="Extra buffer classes for Stable-Baselines3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "stable_baselines3",
    ],
    extras_require={
        "isal": ["isal"],
        "numba": ["numba"],
        "fast": ["sb3_extra_buffers[isal,numba]"],
        "atari": ["gymnasium<1.2.0", "ale-py"],
        "vizdoom": ["gymnasium<1.2.0", "vizdoom"],
    },
    # PyPI package information.
    project_urls={
        "Code": "https://github.com/Trenza1ore/sb3-extra-buffers",
        "Stable-Baselines3": "https://github.com/DLR-RM/stable-baselines3",
        "Stable-Baselines3 - Contrib": "https://github.com/Stable-Baselines-Team/stable-baselines3-contrib",
    },
)
