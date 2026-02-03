import os
import sys
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def plot_full_comparison(raw_path, model_paths, model_names, file_id, pct_range=(0.2, 0.8)):
    num_slices = 5
    num_models = len(model_paths)
    num_rows = 1 + num_models  # Source + Modèles

    # 1. Chargement et calcul des indices
    raw_img = nib.load(raw_path)
    raw_data = raw_img.get_fdata()
    z_max = raw_data.shape[2]
    slice_indices = np.linspace(int(z_max * pct_range[0]), int(z_max * pct_range[1]), num_slices).astype(int)

    # Création de la figure
    fig, axes = plt.subplots(num_rows, num_slices, figsize=(22, 3.5 * num_rows))
    fig.suptitle(f"Analyse Qualitative : {file_id}", fontsize=20, y=0.98)

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
            slice_data = np.rot90(data[:, :, idx])

            # Affichage
            im = ax.imshow(slice_data, cmap=current_cmap,
                           vmin=0 if row == 0 else 0,
                           vmax=None if row == 0 else 4,
                           interpolation='nearest')

            # Titres des colonnes (seulement sur la première ligne)
            if row == 0:
                ax.set_title(f"Coupe {idx}\n({int((idx / z_max) * 100)}%)", fontsize=11, fontweight='bold')

            # --- AFFICHAGE DU NOM DU MODÈLE (L'astuce est ici) ---
            if col == 0:
                # On utilise annotate pour placer le texte précisément à gauche de l'axe
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
    plt.savefig("segmentation_comparison_fixed.png")


# --- Configuration ---
model_paths = [
    "tmp_borgne_data/results_segmentations/seg_Borgne_ses06.nii.gz",
    "tmp_borgne_data/results_segmentations_diff/seg_Borgne_ses06.nii.gz",
    "tmp_borgne_data/results_segmentations_nnunet_longi/Borgne_ses06.nii.gz"
]
raw_path = os.path.join(cfg.DATA_PATH, "Borgne", "ses06", "recons_rhesus/recon_template_space", "srr_template_debiased.nii.gz")
names = ["LongiSeg", "LongiSegDiff", "nnUNetLongi"]

plot_full_comparison(raw_path, model_paths, names, "Borgne 06")