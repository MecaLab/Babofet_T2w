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
slice_idx = 50  # Coupe axiale
y = 100  # Ligne horizontale à y = 100

# Points de départ et d’arrivée de la ligne
x1, x2 = 50, 150  # Début et fin de la ligne

# Extraire le profil d'intensité dans les 2 volumes
intensity1 = profile_line(data1[:, :, slice_idx], (y, x1), (y, x2))
intensity2 = profile_line(data2_resampled[:, :, slice_idx], (y, x1), (y, x2))

# Comparer les deux profils
plt.figure(figsize=(8, 4))
plt.plot(intensity1, label="Original", linestyle="dashed")
plt.plot(intensity2, label="Resampled", linestyle="solid")
plt.xlabel("Position le long de la ligne")
plt.ylabel("Intensité")
plt.legend()
plt.title("Comparaison des profils d'intensité")
plt.tight_layout()
plt.savefig("tmp.png")
