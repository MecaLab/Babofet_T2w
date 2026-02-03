import os
import sys
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

def plot_full_comparison(raw_path, model_paths, model_names, file_id, pct_range=(0.3, 0.75)):
    """
    raw_path: chemin du fichier NIfTI original (le volume source)
    model_paths: liste des 3 chemins vers les segmentations
    """
    num_slices = 7

    # 1. Chargement des données
    raw_data = nib.load(raw_path).get_fdata()
    z_max = raw_data.shape[2]

    # Calcul des indices selon les pourcentages
    slice_indices = np.linspace(int(z_max * pct_range[0]), int(z_max * pct_range[1]), num_slices).astype(int)

    # On crée 4 lignes (1 Source + 3 Modèles)
    fig, axes = plt.subplots(4, num_slices, figsize=(22, 12))
    fig.suptitle(f"Comparaison Anatomique : {file_id}", fontsize=22, y=0.98)

    cmap_seg = plt.get_cmap('tab10', 5)

    # --- LIGNE 1 : VOLUME SOURCE (RAW) ---
    for col in range(num_slices):
        ax = axes[0, col]
        idx = slice_indices[col]
        slice_raw = np.rot90(raw_data[:, :, idx])

        # Affichage en nuances de gris pour le volume brut
        ax.imshow(slice_raw, cmap='gray')
        ax.set_title(f"Coupe {idx} ({int((idx / z_max) * 100)}%)", fontsize=12)
        if col == 0:
            ax.set_ylabel("SOURCE (IRM/CT)", fontsize=14, fontweight='bold', rotation=0, labelpad=80, va='center')
        ax.axis('off')

    # --- LIGNES 2, 3, 4 : MODÈLES ---
    for row_idx, m_path in enumerate(model_paths):
        current_row = row_idx + 1  # +1 car la ligne 0 est la source
        seg_data = nib.load(m_path).get_fdata()

        for col in range(num_slices):
            ax = axes[current_row, col]
            idx = slice_indices[col]
            slice_seg = np.rot90(seg_data[:, :, idx])

            im = ax.imshow(slice_seg, cmap=cmap_seg, vmin=0, vmax=4, interpolation='nearest')

            if col == 0:
                ax.set_ylabel(model_names[row_idx], fontsize=14, fontweight='bold', rotation=0, labelpad=80,
                              va='center')
            if col == 0:
                ax.set_ylabel(model_names[row_idx], fontsize=14, fontweight='bold', rotation=0, labelpad=60, va='center')
            ax.axis('off')

    # Barre de couleur uniquement pour les segmentations
    cbar_ax = fig.add_axes([0.92, 0.2, 0.015, 0.6])
    cbar = fig.colorbar(im, cax=cbar_ax, ticks=range(5))
    cbar.ax.set_yticklabels(['Label 0 (BG)', 'Label 1 (CSF)', 'Label 2 (WM)', 'Label 3 (GM)', 'Label 4 (Ventricles)'])

    plt.subplots_adjust(left=0.18, right=0.9, top=0.85, bottom=0.15, wspace=0.05, hspace=0.15)
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