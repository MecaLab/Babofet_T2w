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

vol1_data = vol1.get_fdata()
vol2_data = vol2.get_fdata()

affine_matrix_vol1 = vol1.affine
affine_matrix_vol2 = vol2.affine

shape1 = vol1_data.shape
shape2 = vol2_data.shape

# Déterminer le nombre de coupes sagittales
# Calculer l'indice du milieu de l'axe sagittal pour le volume 1
mid_sagittal_index1 = shape1[1] // 2

# Indices axiaux à afficher
axial_indices = [50, 60, 70]

# Afficher les coupes sagittales pour chaque indice axial
for axial_index in axial_indices:
    # Coordonnées du voxel au milieu de l'axe sagittal et à l'indice axial donné pour le volume 1
    voxel_coords1 = np.array([shape1[0] // 2, shape1[1] // 2, mid_sagittal_index1, 1])
    voxel_coords1[1] = axial_index  # Mettre à jour la composante axiale

    # Convertir en coordonnées mondiales
    world_coords = affine_matrix_vol1 @ voxel_coords1

    # Convertir les coordonnées mondiales en coordonnées de voxels dans le volume 2
    voxel_coords2 = np.linalg.inv(affine_matrix_vol2) @ world_coords
    voxel_coords2 = np.round(voxel_coords2[:3]).astype(int)

    # Vérifier que les coordonnées sont dans les limites du volume 2
    if (0 <= voxel_coords2[2] < shape2[2]) and (0 <= voxel_coords2[1] < shape2[1]):
        plt.figure(figsize=(10, 5))

        plt.subplot(1, 2, 1)
        plt.imshow(vol1_data[:, axial_index, :].T, cmap='gray', origin='lower')
        plt.title(f'Volume 1 - Axial Slice {axial_index}')
        plt.axis('off')

        plt.subplot(1, 2, 2)
        plt.imshow(vol2_data[:, voxel_coords2[1], :].T, cmap='gray', origin='lower')
        plt.title(f'Volume 2 - Axial Slice {voxel_coords2[1]}')
        plt.axis('off')

plt.savefig("tmp.png")
plt.close()