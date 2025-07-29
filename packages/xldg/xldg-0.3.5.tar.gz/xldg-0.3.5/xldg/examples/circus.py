import os

from xldg.data import Path, MeroX, Domain, Fasta, CrossLink
from xldg.graphics import CircosConfig, Circos

CWD = os.path.join(os.getcwd(), 'tests', 'files', 'graphics', 'circos_test')
fasta_single_path = os.path.join(os.getcwd(), 'tests', 'files', 'data', 'fasta', 'ribosom_E_coli_K12.fas')
fasta_dataset = Fasta.load_data(fasta_single_path, 'Custom', True)
for x in fasta_dataset:
    print(x.raw_header)


# Domain Files Directory
DFD = os.path.join(os.getcwd(), 'tests', 'files', 'data', 'dmn')
domain_path = Path.list_given_type_files(DFD, 'dmn')
domains = Domain.load_data(domain_path)
for x in domains:
    print(x.gene)

merox_data = os.path.join(os.getcwd(), 'tests', 'files', 'data', 'merox') 
zhrm_folder_path = Path.list_given_type_files(merox_data, 'zhrm')
folder_content = MeroX.load_data(zhrm_folder_path, 'DSBU')
combined_data = CrossLink.combine_all(folder_content)
filtered_data = CrossLink.filter_by_score(combined_data, min_score=30)

config = CircosConfig(fasta_dataset, 
                        plot_domain_legend = False, 
                        plot_protein_ids = False, 
                        plot_counter = False,
                        plot_xl_legend = False)
circos = Circos(combined_data, config)

folder = os.path.join(os.getcwd(), 'examples')
save_path = os.path.join(folder, "circos_basic.svg")
circos.save(save_path)

