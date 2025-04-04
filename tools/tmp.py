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
slice_idx = data1.shape[1]//2  # Indice de la coupe

# Identifier les lignes entièrement à l'intérieur du brainmask
valid_y = []
height, width = mask1_data[:, :, slice_idx].shape

indices = [50, 70, 90, 110]
for idx in indices:
    line_mask = mask1_data[:, slice_idx, idx]  # Extraire la ligne dans le brainmask
    if np.all(line_mask):  # Vérifier si toute la ligne est dans le brainmask
        valid_y.append(idx)

# Sélectionner des lignes bien réparties
n_lines = 4  # Nombre de lignes à tracer
if len(valid_y) >= n_lines:
    selected_y = np.linspace(min(valid_y), max(valid_y), n_lines, dtype=int)  # Échantillonnage uniforme
else:
    selected_y = valid_y  # Si moins de n_lines, prendre toutes les lignes disponibles

print(f"✅ Lignes sélectionnées à l'intérieur du brainmask: {selected_y}")

# Nombre de lignes valides
n_rows = len(selected_y)

# Définir les bornes de la ligne horizontale (limites valides dans le brainmask)
x1, x2 = np.where(mask1_data[:, slice_idx, :].sum(axis=0) > 0)[0][[0, -1]]  # Trouver les bords du cerveau

# 5️⃣ Tracer les résultats
fig, axes = plt.subplots(n_rows, 3, figsize=(15, 5 * n_rows))

for i, y in enumerate(selected_y):
    # Extraire les profils d'intensité
    intensity1 = profile_line(data1[:, slice_idx, :], (y, x1), (y, x2))
    intensity2 = profile_line(data2_resampled[:, slice_idx, :], (y, x1), (y, x2))

    # 1️⃣ Affichage de la coupe originale avec brainmask
    axes[i, 0].imshow(data1[:, slice_idx, :], cmap="gray")
    axes[i, 0].imshow(mask1_data[:, slice_idx, :], cmap="jet", alpha=0.3)  # Superposition du brainmask
    axes[i, 0].plot([x1, x2], [y, y], 'r-')  # Ligne rouge sur la coupe
    axes[i, 0].set_title(f"Coupe originale (y={y})")

    # 2️⃣ Affichage de la coupe rééchantillonnée avec brainmask
    axes[i, 1].imshow(data2_resampled[:, slice_idx, :], cmap="gray")
    axes[i, 1].imshow(mask2_resampled_data[:, slice_idx, :], cmap="jet", alpha=0.3)  # Superposition du brainmask
    axes[i, 1].plot([x1, x2], [y, y], 'r-')  # Ligne rouge sur la coupe
    axes[i, 1].set_title(f"Coupe rééchantillonnée (y={y})")

    # 3️⃣ Comparaison des profils d’intensité
    axes[i, 2].plot(intensity1, label="Original", linestyle="dashed")
    axes[i, 2].plot(intensity2, label="Resampled", linestyle="solid")
    axes[i, 2].set_xlabel("Position le long de la ligne")
    axes[i, 2].set_ylabel("Intensité")
    axes[i, 2].legend()
    axes[i, 2].set_title(f"Profil d'intensité (y={y})")

# Affichage global
plt.tight_layout()
plt.savefig("tmp.png")
