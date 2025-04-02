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
    return np.round(voxel_coords[:, :3]).astype(int)


modes = ["sagittal", "axial", "coronal"]
idxs = [50, 60, 70, 80]


for view_mode in modes:
    fig, axes = plt.subplots(len(idxs), 3, figsize=(15, 3 * len(idxs)))
    for i, idx in enumerate(idxs):
        if view_mode == 'sagittal':
            voxel_y_index = vol1_data.shape[1] // 2  # Y au centre
            voxel_coords_vol1 = np.array([[vol1_data.shape[0] // 2, voxel_y_index, idx]])
            slice_2d_vol1 = vol1_data[:, voxel_y_index, :]
            mask_2d_vol1 = brainmask1[:, voxel_y_index, :]
            line_position_voxel1 = voxel_coords_vol1[0, 0]
            line_world_coords = voxel_to_world(np.array([[line_position_voxel1, voxel_y_index, 0]]), affine_matrix_vol1)
            voxel_coords_vol2 = world_to_voxel(line_world_coords, affine_matrix_vol2)
            slice_2d_vol2 = vol2_data[:, voxel_coords_vol2[0, 1], :]
            mask_2d_vol2 = brainmask2[:, voxel_coords_vol2[0, 1], :]
            line_position_voxel2 = voxel_coords_vol2[0, 0]

            # Extraire les profils d'intensité en appliquant le brainmask
            intensity_profile_vol1 = slice_2d_vol1[line_position_voxel1, :] * mask_2d_vol1[line_position_voxel1, :]
            intensity_profile_vol2 = slice_2d_vol2[line_position_voxel2, :] * mask_2d_vol2[line_position_voxel2, :]

        elif view_mode == 'coronal':
            voxel_x_index = vol1_data.shape[0] // 2  # X au centre
            voxel_coords_vol1 = np.array([[voxel_x_index, vol1_data.shape[1] // 2, idx]])
            slice_2d_vol1 = vol1_data[voxel_x_index, :, :]
            mask_2d_vol1 = brainmask1[voxel_x_index, :, :]
            line_position_voxel1 = voxel_coords_vol1[0, 1]
            line_world_coords = voxel_to_world(np.array([[voxel_x_index, line_position_voxel1, 0]]), affine_matrix_vol1)
            voxel_coords_vol2 = world_to_voxel(line_world_coords, affine_matrix_vol2)
            slice_2d_vol2 = vol2_data[voxel_coords_vol2[0, 0], :, :]
            mask_2d_vol2 = brainmask2[voxel_coords_vol2[0, 0], :, :]
            line_position_voxel2 = voxel_coords_vol2[0, 1]

            # Extraire les profils d'intensité en appliquant le brainmask
            intensity_profile_vol1 = slice_2d_vol1[:, line_position_voxel1] * mask_2d_vol1[:, line_position_voxel1]
            intensity_profile_vol2 = slice_2d_vol2[:, line_position_voxel2] * mask_2d_vol2[:, line_position_voxel2]

        elif view_mode == 'axial':
            voxel_z_index = idx
            voxel_coords_vol1 = np.array([[vol1_data.shape[0] // 2, vol1_data.shape[1] // 2, voxel_z_index]])
            slice_2d_vol1 = vol1_data[:, :, voxel_z_index]
            mask_2d_vol1 = brainmask1[:, :, voxel_z_index]
            line_position_voxel1 = voxel_coords_vol1[0, 0]
            line_world_coords = voxel_to_world(np.array([[line_position_voxel1, vol1_data.shape[1] // 2, 0]]),
                                               affine_matrix_vol1)
            voxel_coords_vol2 = world_to_voxel(line_world_coords, affine_matrix_vol2)
            slice_2d_vol2 = vol2_data[:, :, voxel_z_index]
            mask_2d_vol2 = brainmask2[:, :, voxel_z_index]
            line_position_voxel2 = voxel_coords_vol2[0, 0]

            # Extraire les profils d'intensité en appliquant le brainmask
            intensity_profile_vol1 = slice_2d_vol1[line_position_voxel1, :] * mask_2d_vol1[line_position_voxel1, :]
            intensity_profile_vol2 = slice_2d_vol2[line_position_voxel2, :] * mask_2d_vol2[line_position_voxel2, :]

        # Affichage des images avec la ligne rouge
        axes[i, 0].imshow(slice_2d_vol1.T, cmap='gray', origin='lower')
        axes[i, 0].set_title(f'Vol 1 - {view_mode.capitalize()} Slice at Z={idx}')
        axes[i, 0].plot([0, slice_2d_vol1.shape[0] - 1], [line_position_voxel1, line_position_voxel1], color='red',
                        linewidth=2)

        axes[i, 1].imshow(slice_2d_vol2.T, cmap='gray', origin='lower')
        axes[i, 1].set_title(f'Vol 2 - {view_mode.capitalize()} Slice at corresponding Z={idx}')
        axes[i, 1].plot([0, slice_2d_vol2.shape[0] - 1], [line_position_voxel2, line_position_voxel2], color='red',
                        linewidth=2)

        # Affichage des profils d'intensité
        axes[i, 2].plot(intensity_profile_vol1, label='Volume with manual BM', color='blue')
        axes[i, 2].plot(intensity_profile_vol2, label='Volume with mattia BM', color='green')
        axes[i, 2].set_title(f'Intensity Profile at Z={idx}')
        axes[i, 2].set_xlabel('Z')
        axes[i, 2].set_ylabel('Intensity')
        axes[i, 2].legend()

    plt.tight_layout()
    plt.savefig(f"tmp_{view_mode}.png")
