import os
import nibabel as nib
import numpy as np
from scipy.ndimage import correlate


subject = "Fabienne"
base_path = f"../data/recons_folder/{subject}/"
session = "01"

vol_1_path = os.path.join(base_path, f"ses{session}/manual_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline.nii.gz")
vol_2_path = os.path.join(base_path, f"ses{session}/manual_brainmask/exp_param", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_T-1_pipeline.nii.gz")

volume1_data = nib.load(vol_1_path).get_fdata()
volume2_data = nib.load(vol_2_path).get_fdata()

volume1_data = (volume1_data - np.mean(volume1_data)) / np.std(volume1_data)
volume2_data = (volume2_data - np.mean(volume2_data)) / np.std(volume2_data)

print(volume1_data.flatten().shape)
print(volume2_data.flatten().shape)

# Calculer la corrélation croisée
correlation = correlate(volume1_data.flatten(), volume2_data.flatten())

# Normaliser la corrélation croisée
correlation_normalized = correlation / np.sqrt(np.sum(volume1_data**2) * np.sum(volume2_data**2))

print("Corrélation croisée normalisée :", correlation_normalized)