import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt


def world_to_voxel(world_coords, affine_matrix):
    inv_affine_matrix = np.linalg.inv(affine_matrix)
    homogeneous_coords = np.concatenate([world_coords, np.ones((world_coords.shape[0], 1))], axis=1)
    voxel_coords = np.dot(inv_affine_matrix, homogeneous_coords.T).T
    return voxel_coords[:, :3]


subject = "Aziza"
base_path = f"../data/recons_folder/{subject}/"
session = "01"

vol_1_path = os.path.join(base_path, f"ses{session}/manual_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline.nii.gz")
mask_1_path = os.path.join(base_path, f"ses{session}/manual_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline_mask.nii.gz")
vol_2_path = os.path.join(base_path, f"ses{session}/mattia_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_mattia_bm_pipeline.nii.gz")
mask_2_path = os.path.join(base_path, f"ses{session}/mattia_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_mattia_bm_pipeline_mask.nii.gz")

volume1_data = nib.load(vol_1_path).get_fdata()
volume2_data = nib.load(vol_2_path).get_fdata()

mask1_data = nib.load(mask_1_path).get_fdata()
mask2_data = nib.load(mask_2_path).get_fdata()

affine_matrix1 = volume1_data.affines

world_z_coord = 30  # Remplacez par la coordonnée Z souhaitée
world_coords = np.array([
    [0, 0, world_z_coord],
    [volume1_data.shape[0]-1, volume1_data.shape[1]-1, world_z_coord]
])

voxel_coords = world_to_voxel(world_coords, affine_matrix1)


slice_z_index = int(round(voxel_coords[0, 2]))
slice_2d = volume1_data[:, :, slice_z_index]

# Afficher la tranche 2D
plt.imshow(slice_2d.T, cmap='gray', origin='lower')
plt.title(f'Slice at Z = {world_z_coord} (world coordinates)')
plt.xlabel('X')
plt.ylabel('Y')
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
