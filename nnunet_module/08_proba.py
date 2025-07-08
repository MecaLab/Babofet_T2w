import os
import numpy as np
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":

    dataset_id = 3
    output_folder = f"/scratch/lbaptiste/Babofet_T2w/snapshots/nnunet_res/pred_dataset_{dataset_id}"

    for file in os.listdir(output_folder):
        if file.endswith(".nii.gz"):
            seg_path = os.path.join(output_folder, file)
            npz_path = os.path.join(output_folder, file.replace(".nii.gz", ".npz"))

            npz_data = np.load(npz_path)

            print(npz_data.keys())

            break




