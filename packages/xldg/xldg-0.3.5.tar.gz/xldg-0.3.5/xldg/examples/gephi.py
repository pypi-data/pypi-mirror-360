import os
from xldg.data import Path, MeroX, CrossLink, ProteinChainDataset

def _read_file(file_path: str, delete: bool = False):
    content = None
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if delete: 
        os.remove(file_path)
    return content


CWD = os.path.join(os.getcwd(), "tests", "files", "data", "crosslink_test")
# Test Data Folder
TDF = os.path.join(os.getcwd(), "tests", "files", "data", "merox")

chimerax_folder = os.path.join(CWD, 'chimerax')
gephi_folder = os.path.join(CWD, 'gephi')

zhrm_folder_path = Path.list_given_type_files(TDF, 'zhrm')
folder_content = MeroX.load_data(zhrm_folder_path, 'DSBU')
combined_dataset = CrossLink.combine_all(folder_content)

monomer_content = Path.read_to_string(os.path.join(CWD, "monomer.pcd"))
dimer_content = Path.read_to_string(os.path.join(CWD, "dimer.pcd"))
        
pcd_monomer = ProteinChainDataset(monomer_content)
pcd_dimer = ProteinChainDataset(dimer_content)
        
save_monomer = "aais_for_gephi_test_monomer.gexf"
save_dimer = "aais_for_gephi_test_dimer.gexf"
        
combined_dataset.export_aais_for_gephi(pcd_monomer, gephi_folder, save_monomer)
combined_dataset.export_aais_for_gephi(pcd_dimer, gephi_folder, save_dimer)

monomer_sample_path = os.path.join(gephi_folder, save_monomer)
monomer_reference_path = os.path.join(gephi_folder, "aais_for_gephi_reference_monomer.gexf")

dimer_sample_path = os.path.join(gephi_folder, save_dimer)
dimer_reference_path = os.path.join(gephi_folder, "aais_for_gephi_reference_dimer.gexf")

monomer_sample = _read_file(monomer_sample_path)
monomer_reference = _read_file(monomer_reference_path)

dimer_sample = _read_file(dimer_sample_path)
dimer_reference = _read_file(dimer_reference_path)

print(dimer_sample == dimer_reference)
print(monomer_sample == monomer_reference)
