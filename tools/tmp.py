import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

subject = "Fabienne"
base_path = f"../data/recons_folder/{subject}/"
sessions = ["01", "05", "09"]


# Fonction pour obtenir les limites de la ROI en fonction du brainmask
def get_roi_bounds(mask_slice):
    coords = np.argwhere(mask_slice)
    x_min, y_min = coords.min(axis=0)
    x_max, y_max = coords.max(axis=0)
    return x_min, x_max, y_min, y_max


for session in sessions:
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

    # Déterminer le nombre de coupes sagittales
    # Calculer l'indice du milieu de l'axe sagittal pour le volume 1
    mid_sagittal_index1 = shape1[1] // 2
    mid_sagittal_index2 = shape2[1] // 2

    # Indices axiaux (z) à afficher
    axial_indices = [50, 60, 70]

    # Afficher les coupes sagittales et les profils d'intensité pour chaque indice axial dans un format de len(axial_indices) lignes et 3 colonnes
    plt.figure(figsize=(15, 10))

    for i, axial_index in enumerate(axial_indices):
        # Volume 1
        plt.subplot(len(axial_indices), 3, 3 * i + 1)
        sagittal_slice1 = data1[:, mid_sagittal_index1, :]
        plt.imshow(sagittal_slice1.T, cmap='gray', origin='lower')
        plt.axhline(y=axial_index, color='r', linestyle='--')
        plt.title(f'Volume 1 - Sagittal Slice {mid_sagittal_index1}, Axial Index {axial_index}')

        # Volume 2
        plt.subplot(len(axial_indices), 3, 3 * i + 2)
        sagittal_slice2 = data2[:, mid_sagittal_index2, :]
        plt.imshow(sagittal_slice2.T, cmap='gray', origin='lower')
        plt.axhline(y=axial_index, color='r', linestyle='--')
        plt.title(f'Volume 2 - Sagittal Slice {mid_sagittal_index2}, Axial Index {axial_index}')

        # Profil d'intensité
        plt.subplot(len(axial_indices), 3, 3 * i + 3)
        intensity_profile1 = data1[:, mid_sagittal_index1, axial_index]
        intensity_profile2 = data2[:, mid_sagittal_index2, axial_index]
        plt.plot(intensity_profile1, label='Volume 1')
        plt.plot(intensity_profile2, label='Volume 2')
        plt.title(f'Intensity Profile - Axial Index {axial_index}')
        plt.xlabel('Voxel Index')
        plt.ylabel('Intensity')
        plt.legend()

    plt.tight_layout()
    plt.savefig(png_filename)
    plt.close()