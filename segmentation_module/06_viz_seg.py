import os
import sys
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def plot_full_comparison(raw_path, model_paths, model_names, file_id, output, axis=2, pct_range=(0.2, 0.8)):
    axis_names = {0: "SAGITTAL", 1: "CORONAL", 2: "AXIAL"}
    num_slices = 7
    num_models = len(model_paths)
    num_rows = 1 + num_models  # Source + Modèles
    if not os.path.exists(output):
        os.makedirs(output)
    output_filename = os.path.join(output, f"segmentation_comparison_{axis_names[axis]}_{file_id}.png")

    # 1. Chargement et calcul des indices
    raw_img = nib.load(raw_path)
    raw_data = raw_img.get_fdata()
    z_max = raw_data.shape[2]
    slice_indices = np.linspace(int(z_max * pct_range[0]), int(z_max * pct_range[1]), num_slices).astype(int)

    # Création de la figure
    fig, axes = plt.subplots(num_rows, num_slices, figsize=(22, 3.5 * num_rows))
    fig.suptitle(f"Vue {axis_names[axis]} - {file_id}", fontsize=22, y=0.98, fontweight='bold')

    cmap_seg = plt.get_cmap('tab10', 5)

    # On prépare une liste de tous les noms pour les lignes
    all_row_names = ["IMAGE SOURCE"] + model_names

    for row in range(num_rows):
        # On charge la donnée selon la ligne
        if row == 0:
            data = raw_data
            current_cmap = 'gray'
        else:
            data = nib.load(model_paths[row - 1]).get_fdata()
            current_cmap = cmap_seg

        for col in range(num_slices):
            ax = axes[row, col]
            idx = slice_indices[col]

            if axis == 0:
                slice_data = data[idx, :, :]
            elif axis == 1:
                slice_data = data[:, idx, :]
            else:
                slice_data = data[:, :, idx]

            slice_data = np.rot90(slice_data)

            im = ax.imshow(slice_data, cmap=current_cmap,
                           vmin=0 if row == 0 else 0,
                           vmax=None if row == 0 else 4,
                           interpolation='nearest')

            if row == 0:
                ax.set_title(f"Coupe {idx}\n", fontsize=11, fontweight='bold')

            if col == 0:
                ax.annotate(all_row_names[row], xy=(0, 0.5), xycoords='axes fraction',
                            xytext=(-20, 0), textcoords='offset points',
                            ha='right', va='center', fontsize=14, fontweight='bold')

            ax.axis('off')

    # Ajustement manuel des marges pour laisser de la place à GAUCHE (left=0.2)
    plt.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.1, wspace=0.05, hspace=0.2)

    # Barre de légende
    cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.4])
    fig.colorbar(plt.cm.ScalarMappable(cmap=cmap_seg, norm=plt.Normalize(0, 4)),
                 cax=cbar_ax, ticks=range(5))
    plt.savefig(output_filename, dpi=300)


if __name__ == "__main__":
    subjects = {
        "Borgne": [
            "ses06",
            "ses07",
            "ses08",
            "ses09",
            "ses10"
        ]
    }

    for subject in subjects:
        for session in subjects[subject]:
            print(f"Processing subject {subject}, session {session}...")
            model_paths = [
                f"tmp_borgne_data/results_segmentations/seg_{subject}_{session}.nii.gz",
                f"tmp_borgne_data/results_segmentations_diff/seg_{subject}_{session}.nii.gz",
                f"tmp_borgne_data/results_segmentations_nnunet_longi/{subject}_{session}.nii.gz",
                f"inference_all/12_segmentations/{subject}_{session}.nii.gz",
            ]
            raw_path = os.path.join(cfg.DATA_PATH, subject, session, "recons_rhesus/recon_template_space", "srr_template_debiased.nii.gz")
            names = ["LongiSeg", "LongiSegDiff", "nnUNetLongi", "BestnnUNet"]

            for a in [2, 1, 0]: # Axial, Coronal, Sagittal
                print(f"\tProcessing axis {a}...")
                plot_full_comparison(raw_path, model_paths, names, f"{subject}_{session}", output="snapshots/model_comparison", axis=a, pct_range=(0.30, 0.70))
