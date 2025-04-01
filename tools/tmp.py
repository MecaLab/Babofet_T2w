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

volume1_data = nib.load(vol_1_path).get_fdata()
volume2_data = nib.load(vol_2_path).get_fdata()

mask1_data = nib.load(mask_1_path).get_fdata()
mask2_data = nib.load(mask_2_path).get_fdata()

print(volume1_data.shape)
print(volume2_data.shape)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8), facecolor="white")

ax1.imshow(volume1_data[:, volume1_data.shape[1]//2, :], cmap="gray")
middle_x = volume1_data.shape[2] // 2
ax1.plot([middle_x, middle_x], [0, volume1_data.shape[0]-1], color='red', linewidth=2)

ax2.imshow(volume2_data[:, volume2_data.shape[1]//2, :], cmap="gray")

plt.tight_layout()
plt.savefig("tmp.png")
