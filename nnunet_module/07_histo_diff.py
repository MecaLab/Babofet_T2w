import os
import sys
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

if __name__ == "__main__":

    path_1 = "/scratch/lbaptiste/Babofet_T2w/snapshots/nnunet_res/pred_dataset_3"
    path_2 = "/scratch/lbaptiste/Babofet_T2w/snapshots/nnunet_res/pred_dataset_4"

    label_names = {1: "CSF", 2: "WM", 3: "GM", 4: "Ventricule"}

    for file_1, file_2 in zip(os.listdir(path_1), os.listdir(path_2)):
        if file_1.endswith(".nii.gz") and file_2.endswith(".nii.gz"):

            mask1 = nib.load(os.path.join(path_1, file_1)).get_fdata()
            mask2 = nib.load(os.path.join(path_2, file_2)).get_fdata()

            mask1_fg = mask1[mask1 > 0]
            mask2_fg = mask2[mask1 > 0]

            diff = mask1_fg - mask2_fg

            plt.figure(figsize=(8, 4))
            plt.hist(diff, bins=np.arange(diff.min(), diff.max() + 2) - 0.5, color='lightcoral', edgecolor='black')
            plt.title("Histogramme des différences (mask1 - mask2)")
            plt.xlabel("Différences de labels (mask1 - mask2)")
            plt.ylabel("Nombre de voxels")
            plt.grid(True)
            plt.xticks(np.arange(diff.min(), diff.max() + 1))
            output_fig = os.path.join(cfg.BASE_PATH, f"Babofet_T2w/snapshots/nnunet_res/histo_diff_{file_1}.png")
            plt.tight_layout()
            plt.savefig(output_fig)

            # 2. Matrice de confusion entre les deux masques (hors background)
            cm = confusion_matrix(mask1_fg, mask2_fg, labels=[1, 2, 3, 4])

            plt.figure(figsize=(6, 5))
            sns.heatmap(cm, annot=True, fmt='d', cmap="Blues", xticklabels=label_names.values(), yticklabels=label_names.values())
            plt.xlabel("Prédiction modèle 2")
            plt.ylabel("Prédiction modèle 1")
            plt.title("Matrice de confusion entre masques (sans background)")
            output_fig = os.path.join(cfg.BASE_PATH, f"Babofet_T2w/snapshots/nnunet_res/heatmap_diff_{file_1}.png")
            plt.tight_layout()
            plt.savefig(output_fig)
            plt.close()
            break