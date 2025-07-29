import os
from xldg.data import Path, MeroX, CrossLink, ProteinStructure, ProteinChain, Domain, Fasta
from xldg.graphics import Circos, CircosConfig
import os
from xldg.data import Path, MeroX, CrossLink, ProteinStructure, ProteinChain
from xldg.graphics import VennConfig, Venn2, Venn3

if __name__ == "__main__":
    # Circos
    cwd = os.path.join(r'D:\2025-04-03_Meeting-Oleksandr\ZHRM\Shp2\unselected')
    chimera_export = os.path.join(cwd, 'ChimeraX')
    pcd_path = os.path.join(cwd, "Shp2.pcd")
    pcd = ProteinChain.load_data(pcd_path)
    monomer_path = os.path.join(cwd, "Shp2_af2_closed.pdb")
    structure = ProteinStructure.load_data(monomer_path)

    crosslink_files = Path.list_given_type_files(cwd, 'zhrm')
    crosslinks = MeroX.load_data(crosslink_files, 'DSBU')
    crosslinks = CrossLink.combine_all(crosslinks)
    crosslinks = CrossLink.filter_by_score(crosslinks, 50)
    crosslinks.export_for_chimerax(pcd, 
                                   chimera_export, 
                                   'Shp2',
                                   protein_structure=structure, 
                                   min_distance=10.0, 
                                   max_distance=35.0)

    prediction = structure.predict_crosslinks(pcd, '{K', '{K', 10.0, 35.0, 'DSBU', num_processes=4)
    prediction.export_for_chimerax(pcd, 
                                   chimera_export, 
                                   'prediction3')

    config = VennConfig('Title1', 'Title2', title='Title')
    venn2 = Venn2(crosslinks, prediction, config)
    venn2.save(os.path.join(cwd, 'venn2pred.svg'))
