import os
from xldg.data import Path, MeroX,CrossLink, ProteinStructure, ProteinChain


if __name__ == "__main__":
    cwd = os.path.join(os.getcwd(), 'examples', 'chimerax')

    monomer_path = os.path.join(cwd, "two_monomers_complex.cif")
    pcd_path = os.path.join(cwd, "two_monomers_complex.pcd")
    export_folder = os.path.join(cwd, 'results3')

    crosslink_files = Path.list_given_type_files(cwd, 'zhrm')
    crosslinks = MeroX.load_data(crosslink_files, 'DSBU')
    crosslinks = CrossLink.combine_all(crosslinks)
    crosslinks = CrossLink.remove_interprotein(crosslinks)

    structure = ProteinStructure.load_data(monomer_path)
    pcd = ProteinChain.load_data(pcd_path)

    crosslinks.save_crosslink_counter(cwd, 'experiment.tsv')
    crosslinks.export_for_chimerax(pcd, 
                                   export_folder, 
                                   'IMP', 
                                   protein_structure=structure, 
                                   min_distance=2.0, 
                                   max_distance=15.0)

    prediction = structure.predict_crosslinks(pcd, '{', '{K', 10.0, 35.0, 'DSBU', a_star=True)
    prediction.export_for_chimerax(pcd, export_folder, 'pred', color_valid_distance='#ffba08')