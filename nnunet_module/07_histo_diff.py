import os
import sys
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":


    path_1 = "/scratch/lbaptiste/Babofet_T2w/snapshots/nnunet_res/pred_dataset_3"
    path_2 = "/scratch/lbaptiste/Babofet_T2w/snapshots/nnunet_res/pred_dataset_4"

    labels = [1, 2, 3, 4]  # CSF, WM, GM, Ventricle

    for file_1, file_2 in zip(os.listdir(path_1), os.listdir(path_2)):
        if file_1.endswith(".nii.gz") and file_2.endswith(".nii.gz"):

            seg_1 = nib.load(os.path.join(path_1, file_1)).get_fdata()
            seg_2 = nib.load(os.path.join(path_2, file_2)).get_fdata()

            diff = seg_1 - seg_2

            plt.figure(figsize=(10, 5))
            plt.hist(diff.flatten(), bins=np.arange(diff.min(), diff.max() + 2) - 0.5, color='skyblue',
                     edgecolor='black')
            plt.title("Histogramme des différences entre les masques")
            plt.xlabel("Valeur de (mask1 - mask2)")
            plt.ylabel("Nombre de voxels")
            plt.grid(True)
            plt.xticks(np.arange(diff.min(), diff.max() + 1))
            plt.tight_layout()

            output_fig = os.path.join(cfg.BASE_PATH, f"Babofet_T2w/snapshots/nnunet_res/histo_diff_{file_1}.png")
            plt.savefig(output_fig)