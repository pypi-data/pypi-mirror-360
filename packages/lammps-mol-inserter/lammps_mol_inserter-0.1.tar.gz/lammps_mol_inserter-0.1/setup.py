from setuptools import setup, find_packages

setup(
    name="lammps_mol_inserter",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'ase',
        'lammps',
    ],
    author="Danis Bekmansurov",
    author_email="riodan44a@gmail.com",
    url='https://github.com/silentdan44/LAMMPS-Molecule-Inserter',
    description="Library for inserting molecules into LAMMPS simulation boxes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License"
    ],
)
