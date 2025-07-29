import numpy as np
from ase.io import read
from ase.geometry import wrap_positions


class LammpsData:
    def _parse_counts(self):
        self.num_atom_types = 0
        self.num_bond_types = 0
        self.num_angle_types = 0
        self.num_dihedral_types = 0
        self.num_improper_types = 0

        with open(self.data_file, 'r') as f:
            for line in f:
                if 'atom types' in line:
                    self.num_atom_types = int(line.strip().split()[0])
                elif 'bond types' in line:
                    self.num_bond_types = int(line.strip().split()[0])
                elif 'angle types' in line:
                    self.num_angle_types = int(line.strip().split()[0])
                elif 'dihedral types' in line:
                    self.num_dihedral_types = int(line.strip().split()[0])
                elif 'improper types' in line:
                    self.num_improper_types = int(line.strip().split()[0])


class Matrix(LammpsData):
    def __init__(self, data_file):
        self.data_file = data_file
        self.atoms = read(data_file, format='lammps-data')
        self._parse_counts()
        

    def find_empty_bins(self, nbins_x=10, nbins_y=10, nbins_z=10):
        cell = self.atoms.get_cell()
        wrapped_positions = wrap_positions(self.atoms.get_positions(),
                                         cell)

        bins_x = np.linspace(0, cell[0,0], nbins_x+1)
        bins_y = np.linspace(0, cell[1,1], nbins_y+1)
        bins_z = np.linspace(0, cell[2,2], nbins_z+1)

        bin_indices_x = np.digitize(wrapped_positions[:,0], bins_x) - 1
        bin_indices_y = np.digitize(wrapped_positions[:,1], bins_y) - 1
        bin_indices_z = np.digitize(wrapped_positions[:,2], bins_z) - 1

        occupied = np.zeros((nbins_x, nbins_y, nbins_z), dtype=bool)
        for x, y, z in zip(bin_indices_x, bin_indices_y, bin_indices_z):
            occupied[x, y, z] = True

        empty_bin_centers = []
        bin_size_x = cell[0,0] / nbins_x
        bin_size_y = cell[1,1] / nbins_y
        bin_size_z = cell[2,2] / nbins_z

        for x in range(nbins_x):
            for y in range(nbins_y):
                for z in range(nbins_z):
                    if not occupied[x, y, z]:
                        center_x = bins_x[x] + bin_size_x/2 
                        center_y = bins_y[y] + bin_size_y/2 
                        center_z = bins_z[z] + bin_size_z/2 
                        empty_bin_centers.append((center_x, center_y, center_z))

        return empty_bin_centers
    

class Particle(LammpsData):
    def __init__(self, data_file):
        self.data_file = data_file
        self._parse_counts()