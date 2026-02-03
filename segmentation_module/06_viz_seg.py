import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
import random


def get_5_random_slices(path, num_slices=5):
    """Charge le volume et choisit 5 indices de coupes aléatoires."""
    img = nib.load(path)
    data = img.get_fdata()
    z_max = data.shape[2]

    # On évite les tranches extrêmes (souvent vides) en prenant entre 10% et 90%
    slice_indices = np.linspace(z_max * 0.1, z_max * 0.9, num_slices).astype(int)
    # Si tu veux du VRAI aléatoire, décommente la ligne suivante :
    # slice_indices = sorted(random.sample(range(z_max), num_slices))

    return data, slice_indices


def plot_nifti_multi_slices(paths, model_names, file_id):
    # On récupère les indices sur le premier modèle pour synchroniser l'affichage
    first_vol, slice_indices = get_5_random_slices(paths[0])

    fig, axes = plt.subplots(3, 5, figsize=(20, 10))
    fig.suptitle(f"Comparaison Multi-Coupes - {file_id}", fontsize=20)

    cmap = plt.cm.get_cmap('tab10', 5)

    for row, path in enumerate(paths):
        # Pour le premier on a déjà les données, pour les autres on charge
        if row == 0:
            data = first_vol
        else:
            data = nib.load(path).get_fdata()

        for col, slice_idx in enumerate(slice_indices):
            ax = axes[row, col]

            # Extraction et rotation pour l'orientation médicale standard
            slice_data = np.rot90(data[:, :, slice_idx])

            im = ax.imshow(slice_data, cmap=cmap, vmin=0, vmax=4)

            # Titres informatifs
            if row == 0:
                ax.set_title(f"Coupe index: {slice_idx}", fontsize=12)
            if col == 0:
                ax.set_ylabel(model_names[row], fontsize=14, fontweight='bold')

            ax.axis('off')

    # Ajustement de la légende
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    fig.colorbar(im, cax=cbar_ax, ticks=range(5))

    plt.subplots_adjust(left=0.05, right=0.9, top=0.9, bottom=0.1, wspace=0.1, hspace=0.2)
    plt.savefig(f"comparison_multi_slices_{file_id}.png", dpi=300)


# --- Configuration ---
model_paths = [
    "tmp_borgne_data/results_segmentations/seg_Borgne_ses06.nii.gz",
    "tmp_borgne_data/results_segmentations_diff/seg_Borgne_ses06.nii.gz",
    "tmp_borgne_data/results_segmentations_nnunet_longi/Borgne_ses06.nii.gz"
]
names = ["LongiSeg", "LongiSegDiff", "nnUNetLongi"]

plot_nifti_multi_slices(model_paths, names, "Borgne_ses06")