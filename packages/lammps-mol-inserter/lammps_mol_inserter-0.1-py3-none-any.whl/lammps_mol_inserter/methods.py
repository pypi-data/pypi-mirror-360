from lammps import lammps
import numpy as np
from pathlib import Path


class LAMMPSInserter:
    def __init__(self, matrix, particle):
        self.lmp = lammps()
        self.matrix = matrix
        self.particle = particle
        self._initialize_system()
        
    def _initialize_system(self):
        script = f'''
        units real
        atom_style full
        pair_style      lj/cut/coul/long 10
        bond_style      harmonic
        angle_style     harmonic
        dihedral_style  hybrid opls multi/harmonic charmm
        improper_style  cvff 
        special_bonds   amber  
        pair_modify     tail yes mix arithmetic
        kspace_style    pppm 1.0e-4

        read_data {self.matrix.data_file} extra/atom/types {self.particle.num_atom_types} extra/bond/types {self.particle.num_bond_types} extra/angle/types {self.particle.num_angle_types} extra/dihedral/types {self.particle.num_dihedral_types}

        read_data {self.particle.data_file} add append shift 0 0 0 offset {self.matrix.num_atom_types} {self.matrix.num_bond_types} {self.matrix.num_angle_types} {self.matrix.num_dihedral_types} {self.matrix.num_improper_types} group inserted_molecule

        neighbor 2.0 bin
        neigh_modify every 1 delay 5 check yes one 10000
        compute com inserted_molecule com
        variable xcm equal c_com[1]
        variable ycm equal c_com[2]
        variable zcm equal c_com[3]
        run 0
        '''
        self.lmp.commands_string(script)
    
    def get_com_coords(self):
        get_com_script = '''
        uncompute com
        compute com inserted_molecule com
        variable xcm equal c_com[1]
        variable ycm equal c_com[2]
        variable zcm equal c_com[3]
        run 0
        '''
        self.lmp.commands_string(get_com_script)
        xcm = self.lmp.extract_variable("xcm", "all", 0)
        ycm = self.lmp.extract_variable("ycm", "all", 0)
        zcm = self.lmp.extract_variable("zcm", "all", 0)
        return (xcm, ycm, zcm)
    
    def get_pe(self):
        return self.lmp.get_thermo("pe")
    
    def get_displacement(self, target_coords):
        com_coords = self.get_com_coords()
        return tuple(a - b for a, b in zip(target_coords, com_coords))
    
    def displace(self, displacement, bin_coords, output_prefix="", angles=(0, 0, 0)):
        bin_x, bin_y, bin_z = bin_coords
        dis_x, dis_y, dis_z = displacement
        displacement_script = f'''
        displace_atoms inserted_molecule move {dis_x} {dis_y} {dis_z} 
        displace_atoms inserted_molecule rotate {bin_x} {bin_y} {bin_z} {bin_x+1} {bin_y} {bin_z} {angles[0]}
        displace_atoms inserted_molecule rotate {bin_x} {bin_y} {bin_z} {bin_x} {bin_y+1} {bin_z} {angles[1]}
        displace_atoms inserted_molecule rotate {bin_x} {bin_y} {bin_z} {bin_x} {bin_y} {bin_z+1} {angles[2]}
        run 0
        '''
        if output_prefix:
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            displacement_script += f'write_data outputs/{output_prefix}_{bin_x:.1f}_{bin_y:.1f}_{bin_z:.1f}_{angles[0]:.1f}_{angles[1]:.1f}_{angles[2]:.1f}.data\n'
        self.lmp.commands_string(displacement_script)


def bin_inserter(matrix, particle, nbins_x=5, nbins_y=5, nbins_z=5, num_rot=10, out_pref='out'):
    inserter = LAMMPSInserter(matrix, particle)
    empty_bins = matrix.find_empty_bins(nbins_x, nbins_y, nbins_z)
    
    results = []
    for bin_coords in empty_bins:
        for angle_x in np.linspace(0, 360, num_rot):
            for angle_y in np.linspace(0, 360, num_rot):
                for angle_z in np.linspace(0, 360, num_rot):
                    rot = [angle_x, angle_y, angle_z]
                    displacement = inserter.get_displacement(bin_coords)
                    inserter.displace(displacement, bin_coords, output_prefix=out_pref, angles=rot)
                    pe = inserter.get_pe()
                    results.append({
                        'coordinates': bin_coords,
                        'potential_energy': pe,
                        'rotation_x': angle_x,
                        'rotation_y': angle_y,
                        'rotation_z': angle_z
                    })
    
    return results