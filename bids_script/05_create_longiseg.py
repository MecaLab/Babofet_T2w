import os
import shutil
import sys
import pandas as pd
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess
import nibabel as nib
import numpy as np


def format_session_str(sess):
    id_sess = sess[3:]
    return f"ses-{id_sess}"

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
    input_path = os.path.join(cfg.BASE_NIOLON_PATH, "gt_seg")  # need to adapt this later
    output_base_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "longiseg")

    tsv_file = os.path.join(output_base_path, "dseg.tsv")
    if not os.path.exists(tsv_file):
        create_segmentation_mapping_tsv(tsv_file)

    for file in os.listdir(input_path):
        if file.endswith(".nii.gz"):
            print(f"Processing {file}")
            subj_sess = file.split(".")[0]
            subj, sess = subj_sess.split("_")
            sess_formated = format_session_str(sess)

            input_full_path = os.path.join(input_path, file)

            # sub-<sub>_ses-<ses>_seg-braintissues_dseg.nii.gz
            output_file = f"sub-{subj}_{sess_formated}_desc-nnunet_dseg_gt.nii.gz"
            output_path = os.path.join(output_base_path, f"sub-{subj}", sess_formated, "anat")
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            output_full_path = os.path.join(output_path, output_file)
            shutil.copy(input_full_path, output_full_path)

            exit()
