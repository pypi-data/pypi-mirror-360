import os
import pprint
from xldg.data import Path, MeroX, CrossLink, ProteinStructure, ProteinChain, Domain, Fasta
from xldg.graphics import VennConfig, Venn2, Venn3

if __name__ == "__main__":
    # Circos
    cwd = os.path.join(r'\\AGSINZ3\User\Oleksandr\L4\20250428')
    crosslink_files = Path.list_given_type_files(cwd, 'zhrm')
    crosslink_files = Path.sort_filenames_by_first_integer(crosslink_files)
    crosslinks = MeroX.load_data(crosslink_files, 'DSBU')
    crosslinks = CrossLink.filter_by_score(crosslinks, 30)

    second = crosslinks[::2]
    first = crosslinks[1::2]

    second = CrossLink.combine_all(second)
    second = CrossLink.blank_replica(second)

    first = CrossLink.combine_all(first)
    first = CrossLink.blank_replica(first)

    config = VennConfig('Rep1', 'Rep2')
    venn2 = Venn2(first, second, config)
    venn2.save(os.path.join(cwd, 'venn2.svg'))

    combined = CrossLink.combine_all([first, second])
    combined.export_ppis_for_gephi(cwd, 'combined.gexf')

    # venn3 = Venn3(crosslinks[0], crosslinks[1], crosslinks[2], config)
    # venn3.save(os.path.join(cwd, 'venn3.svg'))
