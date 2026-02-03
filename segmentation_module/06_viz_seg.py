import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np


def plot_nifti_comparison_fixed(paths, model_names, file_id, slice_range=(25, 115)):
    """
    Affiche une grille 3x5 de segmentations.
    slice_range: tuple (min, max) pour borner les coupes choisies.
    """
    num_models = len(paths)
    num_slices = 7

    # 1. Sélection des indices de coupes (répartis uniformément entre min et max)
    slice_indices = np.linspace(slice_range[0], slice_range[1], num_slices).astype(int)

    fig, axes = plt.subplots(num_models, num_slices, figsize=(18, 10))
    fig.suptitle(f"Analyse Qualitative : {file_id}", fontsize=20, y=0.95)

    # Palette de couleurs pour 5 classes (Label 0 inclus)
    cmap = plt.get_cmap('tab10', 5)

    for row in range(num_models):
        # Chargement du volume pour le modèle actuel
        data = nib.load(paths[row]).get_fdata()

        for col in range(num_slices):
            ax = axes[row, col]
            idx = slice_indices[col]

            # Extraction et orientation (NIfTI -> Image standard)
            slice_data = np.rot90(data[:, :, idx])

            # Affichage
            im = ax.imshow(slice_data, cmap=cmap, vmin=0, vmax=4)

            if row == 0:
                ax.set_title(f"Coupe {idx}", fontsize=14, pad=10)

            if col == 0:
                ax.set_ylabel(model_names[row], fontsize=14, fontweight='bold', rotation=0, labelpad=60, va='center')

            ax.set_xticks([])
            ax.set_yticks([])

            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color('#CCCCCC')

    cbar_ax = fig.add_axes([0.93, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax, ticks=range(5))
    cbar.set_label('Labels de segmentation', fontsize=12)

    plt.subplots_adjust(left=0.15, right=0.9, top=0.88, bottom=0.1, wspace=0.05, hspace=0.1)
    plt.savefig("segmentation_comparison_fixed.png")


# --- Configuration ---
model_paths = [
    "tmp_borgne_data/results_segmentations/seg_Borgne_ses06.nii.gz",
    "tmp_borgne_data/results_segmentations_diff/seg_Borgne_ses06.nii.gz",
    "tmp_borgne_data/results_segmentations_nnunet_longi/Borgne_ses06.nii.gz"
]
names = ["LongiSeg", "LongiSegDiff", "nnUNetLongi"]

plot_nifti_comparison_fixed(model_paths, names, "Borgne_ses06")