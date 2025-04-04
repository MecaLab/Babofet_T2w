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

mask_data1 = nib.load(mask_1_path).get_fdata()
mask_data2 = nib.load(mask_2_path).get_fdata()

data1 = vol1.get_fdata()
data2 = vol2.get_fdata()

affine1 = vol1.affine
affine2 = vol2.affine

shape1 = data1.shape
shape2 = data2.shape

nii2_resampled = resample_from_to(vol2, vol1)
data2_resampled = nii2_resampled.get_fdata()

# Choisir une coupe et une ligne
# Choisir une coupe et une ligne
slice_idx = 50  # Coupe axiale
y = 100  # Ligne horizontale à y = 100
x1, x2 = 50, 150  # Début et fin de la ligne

# Extraire les profils d'intensité dans les 2 volumes
intensity1 = profile_line(data1[:, :, slice_idx], (y, x1), (y, x2))
intensity2 = profile_line(data2_resampled[:, :, slice_idx], (y, x1), (y, x2))

# Créer une figure avec 3 colonnes
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 1️⃣ Affichage de la coupe originale
axes[0].imshow(data1[:, :, slice_idx], cmap="gray")
axes[0].plot([x1, x2], [y, y], 'r-')  # Ligne rouge sur la coupe
axes[0].set_title("Coupe originale")

# 2️⃣ Affichage de la coupe rééchantillonnée
axes[1].imshow(data2_resampled[:, :, slice_idx], cmap="gray")
axes[1].plot([x1, x2], [y, y], 'r-')  # Ligne rouge sur la coupe
axes[1].set_title("Coupe rééchantillonnée")

# 3️⃣ Affichage du profil d'intensité
axes[2].plot(intensity1, label="Original", linestyle="dashed")
axes[2].plot(intensity2, label="Resampled", linestyle="solid")
axes[2].set_xlabel("Position le long de la ligne")
axes[2].set_ylabel("Intensité")
axes[2].legend()
axes[2].set_title("Comparaison des profils d'intensité")

# Affichage global
plt.tight_layout()
plt.savefig("tmp.png")
