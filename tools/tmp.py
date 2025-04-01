import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt


subject = "Aziza"
base_path = f"../data/recons_folder/{subject}/"
session = "01"

vol_1_path = os.path.join(base_path, f"ses{session}/manual_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline.nii.gz")
mask_1_path = os.path.join(base_path, f"ses{session}/manual_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline_mask.nii.gz")
vol_2_path = os.path.join(base_path, f"ses{session}/mattia_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_mattia_bm_pipeline.nii.gz")
mask_2_path = os.path.join(base_path, f"ses{session}/mattia_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_mattia_bm_pipeline_mask.nii.gz")

vol1 = nib.load(vol_1_path)
vol2 = nib.load(vol_2_path)

vol1_data = vol1.get_fdata()
vol2_data = vol2.get_fdata()

affine_matrix_vol1 = vol1.affine
affine_matrix_vol2 = vol2.affine


# Fonction pour convertir les coordonnées voxel en coordonnées mondiales
def voxel_to_world(voxel_coords, affine_matrix):
    homogeneous_coords = np.concatenate([voxel_coords, np.ones((voxel_coords.shape[0], 1))], axis=1)
    world_coords = np.dot(affine_matrix, homogeneous_coords.T).T
    return world_coords[:, :3]


def world_to_voxel(world_coords, affine_matrix):
    inv_affine_matrix = np.linalg.inv(affine_matrix)
    homogeneous_coords = np.concatenate([world_coords, np.ones((world_coords.shape[0], 1))], axis=1)
    voxel_coords = np.dot(inv_affine_matrix, homogeneous_coords.T).T
    return voxel_coords[:, :3]


# Sélection d'une coupe sagittale
y_index_vol1 = vol1_data.shape[1] // 2

# Conversion en coordonnées mondiales
voxel_coords_vol1 = np.array([[0, y_index_vol1, 0], [0, y_index_vol1, vol1_data.shape[2]-1]])
world_coords = voxel_to_world(voxel_coords_vol1, affine_matrix_vol1)

# Conversion en coordonnées voxel pour le second volume
voxel_coords_vol2 = world_to_voxel(world_coords, affine_matrix_vol2)
y_index_vol2 = int(round(voxel_coords_vol2[0, 1]))

# Extraire les coupes
slice_2d_vol1 = vol1_data[:, y_index_vol1, :]
slice_2d_vol2 = vol2_data[:, y_index_vol2, :]

# Déterminer la position de la ligne rouge dans le premier volume
line_z_index_vol1 = slice_2d_vol1.shape[1] // 2
line_world_coords = voxel_to_world(np.array([[0, y_index_vol1, line_z_index_vol1]]), affine_matrix_vol1)
line_voxel_coords_vol2 = world_to_voxel(line_world_coords, affine_matrix_vol2)
line_z_index_vol2 = int(round(line_voxel_coords_vol2[0, 2]))

# Affichage
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
axes[0].imshow(slice_2d_vol1.T, cmap='gray', origin='lower')
axes[0].set_title(f'Volume 1 - Slice at Y = {y_index_vol1}')
axes[0].set_xlabel('X')
axes[0].set_ylabel('Z')
axes[0].plot([0, slice_2d_vol1.shape[0]-1], [line_z_index_vol1, line_z_index_vol1], color='red', linewidth=2)

axes[1].imshow(slice_2d_vol2.T, cmap='gray', origin='lower')
axes[1].set_title(f'Volume 2 - Slice at corresponding Y')
axes[1].set_xlabel('X')
axes[1].set_ylabel('Z')
axes[1].plot([0, slice_2d_vol2.shape[0]-1], [line_z_index_vol2, line_z_index_vol2], color='red', linewidth=2)


plt.tight_layout()
plt.savefig("tmp.png")
# volume1_data = volume1_data * mask1_data
# volume2_data = volume2_data * mask2_data





"""line_position = 50

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8), facecolor="white")

ax1.imshow(volume1_data[:, volume1_data.shape[1]//2, :], cmap="gray")
ax1.plot([line_position, line_position], [0, volume1_data.shape[0]-1], color='red', linewidth=2)

ax2.imshow(volume2_data[:, volume2_data.shape[1]//2, :], cmap="gray")
ax2.plot([line_position, line_position], [0, volume2_data.shape[0]-1], color='red', linewidth=2)

plt.tight_layout()
plt.savefig("tmp.png")"""
