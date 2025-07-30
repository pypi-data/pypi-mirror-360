from setuptools import setup, find_packages

setup(
    name="aromatools",
    version="0.1.55",
    packages=find_packages(),
    description="Herramientas para el análisis de aromaticidad (HOMA, HOMAc, HOMER)",
    author="Fernando Martínez Villarino",
    author_email="fernandomv5897@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "numpy",
        "networkx",
        "matplotlib",
        "art",
        "ase",
        "pandas",
        "plotly"
    ],
)
