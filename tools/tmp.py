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
axial_indices = [50, 60, 70]

# Afficher les coupes sagittales pour chaque indice axial
for axial_index in axial_indices:
    # Coordonnées du voxel au milieu de l'axe sagittal (y) et à l'indice axial (z) donné pour le volume 1
    voxel_coords1 = np.array([shape1[0] // 2, mid_sagittal_index1, axial_index, 1])

    # Convertir en coordonnées mondiales
    world_coords = affine1 @ voxel_coords1

    # Convertir les coordonnées mondiales en coordonnées de voxels dans le volume 2
    voxel_coords2 = np.linalg.inv(affine2) @ world_coords
    voxel_coords2 = np.round(voxel_coords2[:3]).astype(int)

    # Vérifier que les coordonnées sont dans les limites du volume 2
    if (0 <= voxel_coords2[2] < shape2[2]) and (0 <= voxel_coords2[1] < shape2[1]):
        plt.figure(figsize=(10, 5))

        plt.subplot(1, 2, 1)
        plt.imshow(data1[:, mid_sagittal_index1, axial_index].T, cmap='gray', origin='lower')
        plt.title(f'Volume 1 - Sagittal Slice {mid_sagittal_index1}, Axial Index {axial_index}')
        plt.axis('off')

        plt.subplot(1, 2, 2)
        plt.imshow(data2[:, voxel_coords2[1], voxel_coords2[2]].T, cmap='gray', origin='lower')
        plt.title(f'Volume 2 - Sagittal Slice {voxel_coords2[1]}, Axial Index {voxel_coords2[2]}')
        plt.axis('off')

plt.savefig("tmp.png")
plt.close()