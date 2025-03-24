import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import graycomatrix, graycoprops
from scipy.stats import pearsonr


def calculate_glcm_3d(volume, distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4]):
    """Calcule les matrices de co-occurrence pour un volume 3D en moyennant les résultats des tranches 2D."""
    glcm_list = []
    for slice_2d in volume:
        glcm = graycomatrix(slice_2d.astype(np.uint8), distances=distances, angles=angles, symmetric=True, normed=True)
        glcm_list.append(glcm)
    # Moyenne des matrices de co-occurrence
    glcm_mean = np.mean(glcm_list, axis=0)
    return glcm_mean


def calculate_haralick_features(glcm):
    """Calcule les caractéristiques de Haralick à partir des matrices de co-occurrence."""
    features = {}
    features['dissimilarity'] = graycoprops(glcm, 'dissimilarity')[0, 0]
    features['correlation'] = graycoprops(glcm, 'correlation')[0, 0]
    features['homogeneity'] = graycoprops(glcm, 'homogeneity')[0, 0]
    features['contrast'] = graycoprops(glcm, 'contrast')[0, 0]
    features['ASM'] = graycoprops(glcm, 'ASM')[0, 0]
    features['energy'] = graycoprops(glcm, 'energy')[0, 0]
    return features


def compare_volumes(volume1_masked, volume2_masked):
    """Compare deux volumes 3D en utilisant les caractéristiques de texture."""

    # Calculer les matrices de co-occurrence
    glcm1 = calculate_glcm(volume1_masked)
    glcm2 = calculate_glcm(volume2_masked)

    # Calculer les caractéristiques de Haralick
    features1 = calculate_haralick_features(glcm1)
    features2 = calculate_haralick_features(glcm2)

    # Comparer les caractéristiques
    correlation, _ = pearsonr(list(features1.values()), list(features2.values()))
    return correlation


subject = "Fabienne"
base_path = f"../data/recons_folder/{subject}/"
session = "01"

vol_1_path = os.path.join(base_path, f"ses{session}/manual_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline.nii.gz")
mask_1_path = os.path.join(base_path, f"ses{session}/manual_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline_mask.nii.gz")
vol_2_path = os.path.join(base_path, f"ses{session}/manual_brainmask/exp_param", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_T-1_pipeline.nii.gz")
mask_2_path = os.path.join(base_path, f"ses{session}/manual_brainmask/exp_param", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_T-1_pipeline_mask.nii.gz")

volume1_data = nib.load(vol_1_path).get_fdata()
volume2_data = nib.load(vol_2_path).get_fdata()

mask1_data = nib.load(mask_1_path).get_fdata()
mask2_data = nib.load(mask_2_path).get_fdata()

volume1_data = volume1_data * mask1_data
volume2_data = volume2_data * mask2_data

correlation = compare_volumes(volume1_data, volume2_data)
print(f'Corrélation de Pearson entre les caractéristiques de texture des volumes: {correlation}')