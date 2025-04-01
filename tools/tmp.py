import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt


subject = "Fabienne"
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

plt.imshow(volume1_data[:, volume1_data.shape[1]//2, :], cmap="gray")
plt.savefig("tmp.png")
