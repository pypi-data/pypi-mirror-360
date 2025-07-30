from setuptools import setup, find_packages

setup(
    name="mousehumanizer",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "pynput"
    ],
    author="Matt Kielbasa",
    description="Human-like mouse automation for Windows and Linux",
    url="https://github.com/Matt989MK/mouse-humanizer",
    license="MIT",
) 