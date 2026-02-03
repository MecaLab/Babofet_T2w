import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np


def plot_nifti_comparison_percent(paths, model_names, file_id, pct_range=(0.2, 0.8)):
    """
    pct_range: tuple (min, max) en pourcentage du volume (ex: 0.2 pour 20%)
    """
    num_models = len(paths)
    num_slices = 5

    # 1. Charger le premier volume pour calculer les indices de coupes
    first_img = nib.load(paths[0])
    z_max = first_img.shape[2]

    start_idx = int(z_max * pct_range[0])
    end_idx = int(z_max * pct_range[1])
    slice_indices = np.linspace(start_idx, end_idx, num_slices).astype(int)

    fig, axes = plt.subplots(num_models, num_slices, figsize=(20, 11))
    fig.suptitle(
        f"Comparaison de Segmentation : {file_id}\n(Coupes de {pct_range[0] * 100}% à {pct_range[1] * 100}% du volume)",
        fontsize=18, y=0.97)

    cmap = plt.get_cmap('tab10', 5)

    for row in range(num_models):
        # Chargement sécurisé de chaque modèle
        data = nib.load(paths[row]).get_fdata()

        for col in range(num_slices):
            ax = axes[row, col]
            idx = slice_indices[col]

            # Extraction et rotation pour l'orientation médicale (Radiologique)
            slice_data = np.rot90(data[:, :, idx])

            im = ax.imshow(slice_data, cmap=cmap, vmin=0, vmax=4, interpolation='nearest')

            # --- Labels et Esthétique ---
            if row == 0:
                ax.set_title(f"Coupe {idx}\n({int((idx / z_max) * 100)}%)", fontsize=12, pad=10)

            if col == 0:
                # Placement du nom du modèle à gauche de la ligne
                ax.set_ylabel(model_names[row], fontsize=14, fontweight='bold',
                              rotation=0, labelpad=80, va='center')

            ax.set_xticks([])
            ax.set_yticks([])

    # Légende des classes
    cbar_ax = fig.add_axes([0.92, 0.2, 0.015, 0.6])
    cbar = fig.colorbar(im, cax=cbar_ax, ticks=range(5))
    cbar.ax.set_yticklabels(['Fond (0)', 'Label 1', 'Label 2', 'Label 3', 'Label 4'])

    plt.subplots_adjust(left=0.18, right=0.9, top=0.85, bottom=0.15, wspace=0.05, hspace=0.15)
    plt.savefig("segmentation_comparison_fixed.png")


# --- Configuration ---
model_paths = [
    "tmp_borgne_data/results_segmentations/seg_Borgne_ses06.nii.gz",
    "tmp_borgne_data/results_segmentations_diff/seg_Borgne_ses06.nii.gz",
    "tmp_borgne_data/results_segmentations_nnunet_longi/Borgne_ses06.nii.gz"
]
names = ["LongiSeg", "LongiSegDiff", "nnUNetLongi"]

plot_nifti_comparison_percent(model_paths, names, "Borgne_ses06")