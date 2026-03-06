import os
import sys
import pandas as pd
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess
import nibabel as nib
import numpy as np


def create_segmentation_mapping_tsv(output_filename):
    data = {
        'index': [0, 1, 2, 3, 4],
        'name': ['background', 'csf', 'white_matter', 'grey_matter', 'ventricle'],
        'abbreviation': ['BG', 'CSF', 'WM', 'GM', 'V']
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Save to TSV (tab separated, no index column)
    df.to_csv(output_filename, sep='\t', index=False)

    print(f"Mapping file created: {output_filename}")



if __name__ == "__main__":
    input_path = os.path.join(cfg.BASE_NIOLON_PATH, "pred_dataset_12")  # need to adapt this later
    output_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "nnunet")

    tsv_file = os.path.join(output_path, "dseg.tsv")
    if not os.path.exists(tsv_file):
        create_segmentation_mapping_tsv(tsv_file)

    for file in os.listdir(input_path):
        print(file)