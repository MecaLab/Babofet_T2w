import os
import nibabel as nib
from nibabel.processing import resample_from_to
import numpy as np
import matplotlib.pyplot as plt

subject = "Aziza"
base_path = f"../data/recons_folder/{subject}/"
session = "01"

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

nii2_resampled = resample_from_to(vol2, vol1, interpolation='nearest')
data2_resampled = nii2_resampled.get_fdata()

