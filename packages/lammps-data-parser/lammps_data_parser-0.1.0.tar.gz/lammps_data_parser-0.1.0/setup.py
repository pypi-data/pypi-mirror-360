from setuptools import setup, find_packages

setup(
    name="lammps-data-parser",
    version="0.1.0",
    description="Python library for parsing and editing LAMMPS .data files",
    author="Danis Bekmansurov",
    author_email="riodan44a@gmail.com",
    packages=find_packages(),
    install_requires=[
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    keywords="lammps molecular-dynamics parser",
    project_urls={
        "Source": "https://github.com/silentdan44/lammps-data-parser",
    },
)
