from setuptools import setup, find_packages

setup(
    name="sidemenu",
    version="0.1",
    author="Claudio Morais",
    description="Accordion style side menu with CustomTkinter",
    packages=find_packages(),
    install_requires=[
        "customtkinter"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
