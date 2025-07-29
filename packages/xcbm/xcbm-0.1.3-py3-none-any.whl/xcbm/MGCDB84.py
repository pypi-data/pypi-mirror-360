import os
from pyscf import gto , dft
import numpy as np
import pandas as pd

class MGCDB84_Benchmark:

   def __init__(self, basisset='cc-pvdz', xcfunctional='lda,lda', dataset_path=None, dataset_types=[],package='pyscf'):
        if dataset_path is None:
            raise ValueError("dataset_path cannot be None. Please provide a valid path.")
        if dataset_types is None or len(dataset_types) == 0:
            raise ValueError("Please provide a valid dataset_type.") 
        self.basisset      = basisset
        self.dataset_path  = dataset_path
        self.dataset_types = dataset_types 
        self.xcfunctional  = xcfunctional
        self.package       = package
        if self.package == 'psi4':
            import psi4
        NCED_List = ['A24', 'DS14', 'HB15', 'HSG', 'NBC10', 'S22', 'X40', 'A21x12', 'BzDC215', 'HW30',\
                     'NC15', 'S66x8', '3B-69-DIM', 'AlkBind12', 'CO2Nitrogen16', 'HB49', 'Ionic43',\
                     'H2O6Bind8', 'HW6Cl', 'HW6F', 'FmH2O10', 'shields38', 'SW49Bind345', 'WATER27',\
                     '3B-69-TRIM', 'CE20', 'H2O20Bind10', 'H2O20Bind4']
        All_list =  ['A21x12','A24','AE18','AlkAtom19','AlkIsomer11','AlkIsod14','Bauza30',\
                     'Butanediol65','BzDC215','CT20','DIE60','DS14','EA13','EIE22','FmH2O10','ACONF',\
                     'CYCONF','G21EA','G21IP','NBPRC','WATER27','NHTBH38','HTBH38','BH76RC','DBH24',\
                     'H2O6Bind8','HB15','HSG','HW30','HW6Cl','HW6F','IP13','NBC10','NC15','Pentane14',\
                     'RG10','S22','S66x8','Shields38','Styrene45','SW49Rel345','SW49Bind345','SW49Rel6',\
                     'TA13','BDE99','HAT707','ISOMERIZATION20','SN13','TAE140','X40','XB18','XB51','BHPERI26',\
                     'CR20','CRBH20','AlkBind12','CO2Nitrogen16','HB49','Ionic43','3B-69-DIM','3B-69-TRIM',\
                     'H2O20Bind4','H2O20Rel4','H2O20Bind10','H2O20Rel10','H2O16Rel5','Melatonin52','BSR36',\
                     'HNBrBDE18','PlatonicTAE6','PlatonicIG6','PlatonicHD6','PX13','CE20','WCPT27','WCPT6',\
                     'YMPJ519','20C24']

        self.dataset_type = []
        self.dataset_compute = []
        if 'NCED' in dataset_types:
            self.dataset_compute.extend(NCED_List)
        elif 'All' in dataset_types:
            self.dataset_compute = All_list
        elif len(dataset_types)!=0:
            self.dataset_compute = dataset_types

   def xyz_to_psi4_molecule(self,xyz_file, charge=0, multiplicity=1, units='angstrom'):
       """
       Reads a .xyz file and returns a Psi4 molecule object.
     
       Parameters:
       - xyz_file (str): Path to the .xyz file.
       - charge (int): Total charge of the molecule.
       - multiplicity (int): Spin multiplicity of the molecule.
       - units (str): Units for coordinates ('angstrom' or 'bohr').
     
       Returns:
       - psi4.core.Molecule: Psi4 molecule object.
       """
       with open(xyz_file, 'r') as f:
           lines = f.readlines()
           atom_lines = ''.join(lines[2:])  # skip first two lines
     
       geometry = f"""
       {charge} {multiplicity}
       {atom_lines}
       """
     
       mol = psi4.geometry(f"""
       units {units}
       {geometry}
       """)
       return mol
    

   def compute_rs_energy(self,geometry,charge,multiplicity,basis,xc_functional):
       if self.package == 'psi4':
           mol = self.xyz_to_psi4_molecule(geometry, charge=charge, multiplicity=multiplicity)
           psi4.set_output_file("psi4_output_rks.dat", True)
           psi4.set_options({'basis': basis,
                         'DFT_SPHERICAL_POINTS': 110,
                         'DFT_RADIAL_POINTS'   : 210,
                         'MAXITER'             : 500,  
                          'SCF_TYPE'           :'DIRECT'})
           energy = psi4.properties('SCF',dft_functional=xc_functional, molecule=mol, property=['dipole'])
           #energy = psi4.energy('scf', molecule=mol)
           return energy
       else:
           mol = gto.M(atom=geometry, charge=charge, basis=basis, spin=int((multiplicity-1)))
           mol.verbose = 0
           mf = dft.RKS(mol)
           mf.xc = xc_functional
           energy = mf.kernel()
           return energy
 
   def compute_urs_energy(self,geometry,charge,multiplicity,basis,xc_functional):
       if self.package == 'psi4':
           mol = self.xyz_to_psi4_molecule(geometry, charge=charge, multiplicity=multiplicity)
           psi4.set_output_file("psi4_output_uks.dat", True)
           psi4.set_options({'basis': basis,
                            "reference" : "uhf",
                            'DFT_SPHERICAL_POINTS': 110,
                            'DFT_RADIAL_POINTS'   : 210,
                            'MAXITER'             : 500,
                            'SCF_TYPE'            : 'DIRECT' })
           energy = psi4.properties('SCF',dft_functional=xc_functional, molecule=mol, property=['dipole'])
           #energy = psi4.energy('scf', molecule=mol)
           return energy
       else:
           mol = gto.M(atom=geometry, charge=charge, basis=basis, spin=int((multiplicity-1)))
           mol.verbose = 0
           mf = dft.UKS(mol)
           mf.xc = xc_functional
           energy = mf.kernel()
           return energy
 
   def compute_energy(self):
        directory = self.dataset_path+"/Geometries"
        basis     = self.basisset
        xc_functional     = self.xcfunctional
        structures        = np.array([])
        computed_energies = np.array([])
        self.E_comp_list       = np.array([])
        for ii_d in self.dataset_compute:
           try:
              for filename in os.listdir(directory+"/"+ii_d):
                  filepath = os.path.join(directory+"/"+ii_d, filename)
                  print(filepath)
                  if os.path.isfile(filepath):  
                      with open(filepath, 'r') as file:
                          content = file.readlines()
                          for line in content[1:2]:
                              charge        = int(line.strip().split()[0])
                              multiplicity  = int(line.strip().split()[1])
                  if multiplicity == 1:
                      input_energy = self.compute_rs_energy(geometry=filepath , charge=charge, multiplicity=multiplicity, basis=basis, xc_functional=xc_functional)
                  if multiplicity > 1:
                      input_energy = self.compute_urs_energy(geometry=filepath, charge=charge, multiplicity=multiplicity, basis=basis, xc_functional=xc_functional)
             
                  structures        = np.append(structures,filename[:-4])
                  computed_energies = np.append(computed_energies,input_energy)
              self.E_comp_list       = np.append(self.E_comp_list,ii_d)
           except Exception as e:
               print(f"Error with {ii_d}")
               continue

        return structures, computed_energies
 
   def compute_prediction(self):
        comp_struc , comp_energy = self.compute_energy()
        print('length of comp_struc',  len(comp_struc))
        print('length of comp_energy', len(comp_energy))
        data_set = pd.DataFrame()
        data_set['computed_struc']  = comp_struc
        data_set['computed_energy'] = comp_energy
        computed_predictions = np.array([])
        dp_name = np.array([])
        dp_ref  = np.array([])

        print('E_comp_lost ' , self.E_comp_list)        
        for ii_j in self.E_comp_list:
            data_file = self.dataset_path+"/Reaction_Energy/"+ii_j+".dat"
            with open(data_file,'r') as file:
                lines = file.readlines()
                for line in lines:
                    for s in line.strip().split(',')[0:1]:
                        dp_name = np.append(dp_name,str(s))
                    for s in line.strip().split(',')[-1:]:
                        dp_ref = np.append(dp_ref,float(s))
                    count_odd  = 0
                    count_even = 0
                    temp_list = []
                    for s in line.strip().split(',')[1:-1]:
                        temp_list.append(s)
                    ss = 0
                    j_count = 0
                    while j_count <= (len(temp_list)-1):
                        ss += float(temp_list[j_count]) * float(data_set.loc[data_set['computed_struc'] == temp_list[j_count+1], 'computed_energy'].values[0])
                        j_count+=2
                    computed_predictions = np.append(computed_predictions,float(ss))
        generated_dataset = pd.DataFrame()
        generated_dataset['prop_name']           =   dp_name
        generated_dataset['ref_prediction']      =   dp_ref
        generated_dataset['computed_prediction'] =   computed_predictions 
      
        RMSD_list = self.compute_RMSE(generated_dataset)
        MAD_list = self.compute_MAD(generated_dataset)
        return RMSD_list, MAD_list        
 
   def compute_RMSE(self, inp_data_set=[]):

        if not inp_data_set.empty:
            rmsd_list = []
            for iii in self.E_comp_list:
                filtered_df = inp_data_set[inp_data_set['prop_name'].str.contains(iii, na=False)]
            
                if filtered_df.empty:
                    return None  
            
                msad_b = np.sqrt(np.mean(np.abs(filtered_df['ref_prediction'] - filtered_df['computed_prediction'])**2))   
                rmsd_list.append(msad_b)
            return rmsd_list


   def compute_MAD(self,inp_data_set=[]):

        if not inp_data_set.empty:
            mad_list = []
            for iii in self.E_comp_list:
                filtered_df = inp_data_set[inp_data_set['prop_name'].str.contains(iii, na=False)]
            
                if filtered_df.empty:
                    return None  
            
                mad_b = (np.mean(np.abs(filtered_df['ref_prediction'] - filtered_df['computed_prediction'])))   
                mad_list.append(mad_b)
            return mad_list


   def compute_RMS(self):
        data_file = self.dataset_path+"/DatasetEval.csv"
        with open(data_file,'r') as file:
            lines = file.readlines()
            dp_name = np.array([])
            dp_ref  = np.array([])
            for line in lines:
                for s in line.strip().split(',')[0:1]:
                    dp_name = np.append(dp_name,str(s))
                for s in line.strip().split(',')[-1:]:
                    dp_ref = np.append(dp_ref,float(s))
        generated_dataset = pd.DataFrame()
        generated_dataset['prop_name']           =   dp_name
        generated_dataset['ref_prediction']      =   dp_ref
        
        rmsd_list = []
        for iii in self.dataset_compute:
            filtered_df = generated_dataset[generated_dataset['prop_name'].str.contains(iii, na=False)]
            
            if filtered_df.empty:
                return None  
            if iii == 'A24':
                for ll_name, ll_ener in zip(filtered_df['prop_name'],filtered_df['ref_prediction']):
                    print(' name ', ll_name,' energy ',ll_ener)
            msad_b = np.sqrt(np.mean(np.abs(filtered_df['ref_prediction'])**2))   
            #rmsd_list.append(msad_b)
            print(iii, msad_b)
        return dataset_compute, rmsd_list
