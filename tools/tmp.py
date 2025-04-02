import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

subject = "Aziza"
base_path = f"../data/recons_folder/{subject}/"
session = "09"

vol_1_path = os.path.join(base_path, f"ses{session}/manual_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline.nii.gz")
mask_1_path = os.path.join(base_path, f"ses{session}/manual_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline_mask.nii.gz")

vol_2_path = os.path.join(base_path, f"ses{session}/mattia_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_mattia_bm_pipeline.nii.gz")
mask_2_path = os.path.join(base_path, f"ses{session}/mattia_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_mattia_bm_pipeline_mask.nii.gz")

vol1 = nib.load(vol_1_path)
vol2 = nib.load(vol_2_path)

brainmask1 = nib.load(mask_1_path).get_fdata()
brainmask2 = nib.load(mask_2_path).get_fdata()

data1 = vol1.get_fdata()
data2 = vol2.get_fdata()

affine1 = vol1.affine
affine2 = vol2.affine

shape1 = data1.shape
shape2 = data2.shape

# Déterminer le nombre de coupes sagittales
# Calculer l'indice du milieu de l'axe sagittal pour le volume 1
mid_sagittal_index1 = shape1[1] // 2

# Indices axiaux (z) à afficher
mid_sagittal_index1 = shape1[1] // 2

# Indices axiaux (z) à afficher
axial_indices = [50, 60, 70]

# Afficher les coupes sagittales pour chaque indice axial dans un format de len(axial_indices) lignes et 2 colonnes
plt.figure(figsize=(10, 15))

for i, axial_index in enumerate(axial_indices):
    # Volume 1
    plt.subplot(len(axial_indices), 2, 2 * i + 1)
    sagittal_slice1 = data1[:, mid_sagittal_index1, :]
    plt.imshow(sagittal_slice1.T, cmap='gray', origin='lower')
    plt.axhline(y=axial_index, color='r', linestyle='--')
    plt.title(f'Volume 1 - Sagittal Slice {mid_sagittal_index1}, Axial Index {axial_index}')
    plt.axis('off')

    # Volume 2
    plt.subplot(len(axial_indices), 2, 2 * i + 2)
    sagittal_slice2 = data2[:, mid_sagittal_index1, :]
    plt.imshow(sagittal_slice2.T, cmap='gray', origin='lower')
    plt.axhline(y=axial_index, color='r', linestyle='--')
    plt.title(f'Volume 2 - Sagittal Slice {mid_sagittal_index1}, Axial Index {axial_index}')

plt.tight_layout()
plt.savefig("tmp.png")
plt.close()