# LAMMPS Molecule Inserter

A Python library for inserting molecules into LAMMPS simulation boxes with various orientations and positions, then evaluating their potential energy.

## Algorithm Overview

The LAMMPS Molecule Inserter works by splitting the simulation box into small 3D boxes (bins). It first checks which of these small boxes are empty (no atoms from the host material). Then it tries inserting the molecule at the center of each empty box while rotating it in different directions. For each position and rotation, it calculates the system's energy. Finally, it keeps the best positions where the molecule fits comfortably with lowest energy. This helps quickly find good starting positions for molecules in materials.

## Requirements

 * Python 3.6+
 * numpy
 * ASE (Atomic Simulation Environment)
 * LAMMPS (with Python interface)

## Installation

```bash
pip install lammps_mol_inserter
```

## Usage

```python
from lammps_mol_inserter.io import Matrix, Particle
from lammps_mol_inserter.methods import bin_inserter


matrix = Matrix('matrix.data')
particle = Particle('particle.data')


results = bin_inserter(
    matrix, 
    particle,
    nbins_x=5,      # Number of bins along x-axis
    nbins_y=5,      # along y-axis
    nbins_z=5,      # along z-axis
    num_rot=10,     # Number of rotation steps per axis (0-360°)
    out_pref='out'  # Output file prefix
)

# Sort results by potential energy
sorted_results = sorted(results, key=lambda x: x['potential_energy'])
print("Top 5 lowest energy configurations:")
print(sorted_results[:5])
```

To use different force field styles (pair, bond, angle, etc.), you need to modify the *_initialize_system()* method in the LAMMPSInserter class. This method contains the LAMMPS commands that initialize the simulation environment.
