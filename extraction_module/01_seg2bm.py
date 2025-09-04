import numpy as np
import os
import sys
import nibabel as nib
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

path_in = "/envau/work/meca/data/babofet_DB/2024_new_stuff/nnunet_pred_dataset_7_3000/"
path_out = os.path.join(path_in, "brainmask")

if not os.path.exists(path_out):
    os.makedirs(path_out)

for file in os.listdir(path_in):
    if file.endswith(".nii.gz"):
        print(f"Processing {file}")

        full_path_in = os.path.join(path_in, file)
        full_path_out = os.path.join(path_out, f"bm_{file}")

        img = nib.load(full_path_in)
        data = img.get_fdata()

        brainmask = np.where(data > 0, 1, 0)

        brainmask_img = nib.Nifti1Image(brainmask, img.affine, img.header)
        nib.save(brainmask_img, full_path_out)