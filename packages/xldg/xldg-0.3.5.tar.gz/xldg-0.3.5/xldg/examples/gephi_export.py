from xldg.utils import Path, DatasetUtil
from xldg.xl import ProteinChainDataset

if __name__ == "__main__":
    CWD = r"D:\Test_Lydia\241027_Mix50MBP"
    pcd = ProteinChainDataset(os.path.join(CWD, "monomer.pcd"))

    zhrm_folder_path = Path.list_specified_type_files_from_folder(CWD, '.zhrm')
    folder_content = DatasetUtil.read_all_merox_files(zhrm_folder_path, 'DSBU')
    combined_dataset = DatasetUtil.combine_all_datasets(folder_content)
    filtered_dataset = DatasetUtil.filter_all_by_score([combined_dataset], 60)
    filtered_dataset[0].export_ppis_for_gephi(pcd, CWD, "Lydia1.gexf")
    filtered_dataset[0].export_aais_for_gephi(pcd, CWD, "Lydia2.gexf")
