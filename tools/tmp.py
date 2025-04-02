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

brainmask1 = nib.load(mask_1_path).get_fdata()
brainmask2 = nib.load(mask_2_path).get_fdata()

vol1_data = vol1.get_fdata()
vol2_data = vol2.get_fdata()

"""vol1_data = vol1_data * brainmask1
vol2_data = vol2_data * brainmask2"""

affine_matrix_vol1 = vol1.affine
affine_matrix_vol2 = vol2.affine


# Fonction pour convertir les coordonnées voxel en coordonnées mondiales
def voxel_to_world(voxel_coords, affine_matrix):
    homogeneous_coords = np.concatenate([voxel_coords, np.ones((voxel_coords.shape[0], 1))], axis=1)
    world_coords = np.dot(affine_matrix, homogeneous_coords.T).T
    return world_coords[:, :3]


# Fonction pour convertir les coordonnées mondiales en coordonnées voxel
def world_to_voxel(world_coords, affine_matrix):
    inv_affine_matrix = np.linalg.inv(affine_matrix)
    homogeneous_coords = np.concatenate([world_coords, np.ones((world_coords.shape[0], 1))], axis=1)
    voxel_coords = np.dot(inv_affine_matrix, homogeneous_coords.T).T
    return np.floor(voxel_coords[:, :3]).astype(int)


modes = ["sagittal", "axial", "coronal"]
idxs = [50, 60, 70, 80]


for view_mode in modes:

    fig, axes = plt.subplots(len(idxs), 3, figsize=(15, 3 * len(idxs)))

    for i, idx in enumerate(idxs):
        if view_mode == 'axial':  # Vue AXIALE (XY)
            voxel_coords_vol1 = np.array([[vol1_data.shape[0] // 2, vol1_data.shape[1] // 2, idx]])
        elif view_mode == 'sagittal':  # Vue SAGITTALE (YZ)
            voxel_coords_vol1 = np.array([[vol1_data.shape[0] // 2, idx, vol1_data.shape[2] // 2]])
        elif view_mode == 'coronal':  # Vue CORONALE (XZ)
            voxel_coords_vol1 = np.array([[idx, vol1_data.shape[1] // 2, vol1_data.shape[2] // 2]])

        # Conversion vers le repère du monde
        world_coords = voxel_to_world(voxel_coords_vol1, affine_matrix_vol1)

        # Transformation vers le second volume
        voxel_coords_vol2 = world_to_voxel(world_coords, affine_matrix_vol2)

        # Extraction des coupes
        if view_mode == 'axial':
            slice_2d_vol1 = vol1_data[:, :, idx]
            slice_2d_vol2 = vol2_data[:, :, voxel_coords_vol2[0, 2]]

            mask_2d_vol1 = brainmask1[:, :, idx]
            mask_2d_vol2 = brainmask2[:, :, voxel_coords_vol2[0, 2]]

            line_position = voxel_coords_vol1[0, 0]  # Ligne horizontale en X

        elif view_mode == 'sagittal':
            slice_2d_vol1 = vol1_data[:, idx, :]
            slice_2d_vol2 = vol2_data[:, voxel_coords_vol2[0, 1], :]

            mask_2d_vol1 = brainmask1[:, idx, :]
            mask_2d_vol2 = brainmask2[:, voxel_coords_vol2[0, 1], :]

            line_position = voxel_coords_vol1[0, 0]  # Ligne horizontale en X

        elif view_mode == 'coronal':
            slice_2d_vol1 = vol1_data[idx, :, :]
            slice_2d_vol2 = vol2_data[voxel_coords_vol2[0, 0], :, :]

            mask_2d_vol1 = brainmask1[idx, :, :]
            mask_2d_vol2 = brainmask2[voxel_coords_vol2[0, 0], :, :]

            line_position = voxel_coords_vol1[0, 1]  # Ligne horizontale en Y

        # Extraire les profils d'intensité avec le brainmask
        intensity_profile_vol1 = slice_2d_vol1[line_position, :] * mask_2d_vol1[line_position, :]
        intensity_profile_vol2 = slice_2d_vol2[line_position, :] * mask_2d_vol2[line_position, :]

        # Affichage des images et des profils d'intensité
        axes[i, 0].imshow(slice_2d_vol1.T, cmap='gray', origin='lower')
        axes[i, 0].set_title(f'Vol 1 - {view_mode.capitalize()} Slice {idx}')
        axes[i, 0].plot([0, slice_2d_vol1.shape[1] - 1], [line_position, line_position], color='red', linewidth=2)

        axes[i, 1].imshow(slice_2d_vol2.T, cmap='gray', origin='lower')
        axes[i, 1].set_title(f'Vol 2 - {view_mode.capitalize()} Slice {idx}')
        axes[i, 1].plot([0, slice_2d_vol2.shape[1] - 1], [line_position, line_position], color='red', linewidth=2)

        # Affichage des profils d'intensité
        axes[i, 2].plot(intensity_profile_vol1, label='Volume 1', color='blue')
        axes[i, 2].plot(intensity_profile_vol2, label='Volume 2', color='green')
        axes[i, 2].set_title(f'Intensity Profile - {view_mode.capitalize()} Slice {idx}')
        axes[i, 2].set_xlabel('Position')
        axes[i, 2].set_ylabel('Intensity')
        axes[i, 2].legend()

        plt.tight_layout()
        plt.savefig(f"tmp_{view_mode}.png")
