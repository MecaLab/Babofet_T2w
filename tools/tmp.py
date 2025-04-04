import os
import nibabel as nib
from nibabel.processing import resample_from_to
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import profile_line

subject = "Aziza"
base_path = f"../data/recons_folder/{subject}/"
session = "01"

png_filename = f"comparaison_{subject.lower()}_ses-{session}.png"

vol_1_path = os.path.join(base_path, f"ses{session}/manual_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline.nii.gz")
mask_1_path = os.path.join(base_path, f"ses{session}/manual_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline_mask.nii.gz")

vol_2_path = os.path.join(base_path, f"ses{session}/mattia_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_mattia_bm_pipeline.nii.gz")
mask_2_path = os.path.join(base_path, f"ses{session}/mattia_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_mattia_bm_pipeline_mask.nii.gz")

vol1 = nib.load(vol_1_path)
vol2 = nib.load(vol_2_path)

mask1_data = nib.load(mask_1_path).get_fdata()
mask_data2 = nib.load(mask_2_path)

data1 = vol1.get_fdata()

nii2_resampled = resample_from_to(vol2, vol1)
data2_resampled = nii2_resampled.get_fdata()

mask2_resampled_data = resample_from_to(mask_data2, vol1, order=0).get_fdata()

# Choisir une coupe et une ligne
# Choisir une coupe axiale

slice_idx = data1.shape[2]//2  # Coupe axiale

# Définir plusieurs lignes horizontales à analyser
y_values = [50, 70, 90, 110]  # Plusieurs valeurs de y
x1, x2 = 0, 120  # Début et fin de la ligne

# Déterminer le nombre de lignes
n_rows = len(y_values)

# Créer une figure avec n lignes et 3 colonnes
fig, axes = plt.subplots(n_rows, 4, figsize=(19, 5 * n_rows))

for i, y in enumerate(y_values):
    # Extraire les profils d'intensité pour cette ligne y
    intensity1 = profile_line(data1[:, :, slice_idx], (y, x1), (y, x2))
    intensity2 = profile_line(data2_resampled[:, :, slice_idx], (y, x1), (y, x2))
    intensity_diff = np.subtract(intensity1, intensity2)

    axes[i, 0].imshow(data1[:, :, slice_idx], cmap="gray")
    axes[i, 0].plot([x1, x2], [y, y], 'r-')  # Ligne rouge sur la coupe
    axes[i, 0].set_title(f"Coupe originale (y={y})")

    axes[i, 1].imshow(data2_resampled[:, :, slice_idx], cmap="gray")
    axes[i, 1].plot([x1, x2], [y, y], 'r-')  # Ligne rouge sur la coupe
    axes[i, 1].set_title(f"Coupe rééchantillonnée (y={y})")

    axes[i, 2].plot(intensity1, label="Original", linestyle="dashed")
    axes[i, 2].plot(intensity2, label="Resampled", linestyle="solid")
    axes[i, 2].set_xlabel("Position le long de la ligne")
    axes[i, 2].set_ylabel("Intensité")
    axes[i, 2].legend()
    axes[i, 2].grid()
    axes[i, 2].set_title(f"Profil d'intensité (y={y})")

    axes[i, 3].plot(intensity_diff, label="Difference", color="purple")
    axes[i, 3].set_xlabel("Position le long de la ligne")
    axes[i, 3].set_ylabel("Différence d'intensité")
    axes[i, 3].grid()
    axes[i, 3].set_title(f"Différence (y={y})")

# Affichage global
plt.tight_layout()
plt.savefig("tmp.png")
