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


view_mode = "axial"  # Modifie ici

# Liste des positions où tracer la ligne rouge
idxs = [50, 60, 70, 80]

fig, axes = plt.subplots(len(idxs), 3, figsize=(12, 3 * len(idxs)))

for i, idx in enumerate(idxs):
    if view_mode == "axial":
        # Coupe XY (vue du dessus) -> ligne verticale sur Y
        slice_vol1 = vol1[:, :, idx]
        slice_vol2 = vol2[:, :, idx]
        mask_vol1 = brainmask1[:, :, idx]
        mask_vol2 = brainmask2[:, :, idx]

        line_pos = slice_vol1.shape[1] // 2  # Position au centre en Y
        intensity_profile_vol1 = slice_vol1[:, line_pos] * mask_vol1[:, line_pos]
        intensity_profile_vol2 = slice_vol2[:, line_pos] * mask_vol2[:, line_pos]

    elif view_mode == "sagittal":
        # Coupe YZ (vue de côté) -> ligne verticale sur Z
        slice_vol1 = vol1[vol1.shape[0] // 2, :, :]
        slice_vol2 = vol2[vol2.shape[0] // 2, :, :]
        mask_vol1 = brainmask1[vol1.shape[0] // 2, :, :]
        mask_vol2 = brainmask2[vol2.shape[0] // 2, :, :]

        line_pos = slice_vol1.shape[1] // 2  # Position au centre en Z
        intensity_profile_vol1 = slice_vol1[line_pos, :] * mask_vol1[line_pos, :]
        intensity_profile_vol2 = slice_vol2[line_pos, :] * mask_vol2[line_pos, :]

    elif view_mode == "coronal":
        # Coupe XZ (vue de face) -> ligne verticale sur Z
        slice_vol1 = vol1[:, vol1.shape[1] // 2, :]
        slice_vol2 = vol2[:, vol2.shape[1] // 2, :]
        mask_vol1 = brainmask1[:, vol1.shape[1] // 2, :]
        mask_vol2 = brainmask2[:, vol2.shape[1] // 2, :]

        line_pos = slice_vol1.shape[0] // 2  # Position au centre en X
        intensity_profile_vol1 = slice_vol1[line_pos, :] * mask_vol1[line_pos, :]
        intensity_profile_vol2 = slice_vol2[line_pos, :] * mask_vol2[line_pos, :]

    # Affichage des images et de la ligne rouge
    axes[i, 0].imshow(slice_vol1.T, cmap='gray', origin='lower')
    axes[i, 0].set_title(f'Vol 1 - {view_mode.capitalize()} at idx={idx}')
    axes[i, 0].plot([line_pos, line_pos], [0, slice_vol1.shape[1]-1], color='red', linewidth=2)

    axes[i, 1].imshow(slice_vol2.T, cmap='gray', origin='lower')
    axes[i, 1].set_title(f'Vol 2 - {view_mode.capitalize()} at idx={idx}')
    axes[i, 1].plot([line_pos, line_pos], [0, slice_vol2.shape[1]-1], color='red', linewidth=2)

    # Affichage des profils d'intensité
    axes[i, 2].plot(intensity_profile_vol1, label='Volume with manual BM', color='blue')
    axes[i, 2].plot(intensity_profile_vol2, label='Volume with mattia BM', color='green')
    axes[i, 2].set_title(f'Intensity Profile - {view_mode.capitalize()} at idx={idx}')
    axes[i, 2].set_xlabel('Position')
    axes[i, 2].set_ylabel('Intensity')
    axes[i, 2].legend()

plt.tight_layout()
plt.savefig("tmp.png")
plt.show()
