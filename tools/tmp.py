import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt


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

print(mask1_data.shape)
print(mask2_data.shape)

volume1_data = volume1_data[mask1_data > 0]
volume2_data = volume2_data[mask2_data > 0]

volume1_fft = np.fft.fftn(volume1_data)
volume2_fft = np.fft.fftn(volume2_data)

# Calculer le spectre de puissance
volume1_power_spectrum = np.abs(volume1_fft)**2
volume2_power_spectrum = np.abs(volume2_fft)**2

# Visualiser les spectres de puissance
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.imshow(np.log1p(volume1_power_spectrum[:, :, volume1_power_spectrum.shape[2]//2]), cmap='jet')
plt.title('Spectre de puissance Volume 1')
plt.colorbar()

plt.subplot(1, 2, 2)
plt.imshow(np.log1p(volume2_power_spectrum[:, :, volume2_power_spectrum.shape[2]//2]), cmap='jet')
plt.title('Spectre de puissance Volume 2')
plt.colorbar()

plt.savefig("tmp.png")

# Comparer les spectres de puissance
difference = np.abs(volume1_power_spectrum - volume2_power_spectrum)
total_difference = np.sum(difference)

print("Différence totale entre les spectres de puissance :", total_difference)