"""Generate a masked v
TODO: create a slurm version of this python script
"""

import os
import sys
import numpy as np
import nibabel as nib
from skimage import morphology as smo
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def dilate_binary_mask(mask, nb_dilation):
    """Morphologically dilate a binary brain mask
    Parameters
    ----------
    mask : nib.Nifti1Image
         binary mask

    nb_dilation : int
        number of successive bianry morphological dilation applied on the mask

    Returns
    -------
    nib.Nifti1Image
    dilated binary mask

    """
    dilated_bmask = mask.get_fdata()
    for step in range(nb_dilation):
        dilated_bmask = smo.binary_dilation(dilated_bmask)
    dilated_mask = nib.Nifti1Image(
        dilated_bmask, affine=mask.affine, header=mask.header
    )
    return dilated_mask


def mask_volume(binary_mask, volume):
    """Mask a given volume using a binary mask

    Parameters
    ----------
    binary_mask :  nib.Nifti1Image
        Binary mask used to mask the input volume
    volume :   nib.Nifti1Image
        Volume to mask
    Returns
    -------
    nib.Nifti1Image
        Masked volume
    """
    data = volume.get_fdata()
    bin_mask = binary_mask.get_fdata()
    masked_data = data * bin_mask
    masked_volume = nib.Nifti1Image(
        masked_data.astype(np.float32), volume.affine, header=volume.header
    )
    return masked_volume


def generate_masked_volume(
    path_binary_mask, path_volume, path_masked_volume, nb_dilation
):
    """
    Parameters
    ----------
    path_binary_mask :
    path_volume :
    path_masked_volume :
    nb_dilation :

    Returns
    -------

    """

    binary_mask = nib.load(path_binary_mask)
    #  to be sure the mask does not have an additional channel
    binary_mask = nib.funcs.squeeze_image(binary_mask)
    dilated_binary_mask = dilate_binary_mask(binary_mask, nb_dilation)
    volume = nib.load(path_volume)
    masked_volume = mask_volume(dilated_binary_mask, volume)
    nib.save(masked_volume, path_masked_volume)


if __name__ == "__main__":

    NB_DILATION = 3

    output_DB_path = cfg.DATA_PATH

    sequences = ["haste"]

    subjects = os.listdir(output_DB_path)
    for subject in subjects:
        subject_path = os.path.join(output_DB_path, subject)
        for session in os.listdir(subject_path):
            subject_session_path = os.path.join(subject_path, session)

            if not "recons_rhesus" in os.listdir(subject_session_path): # change 'tmp_exp' to 'recons_pipeline' if needed
                continue

            print(f"Processing {subject} {session}...")
            # reconst_dir = os.path.join(subject_session_path, "recons_pipeline")
            reconst_dir = os.path.join(subject_session_path, "recons_rhesus")

            recon_template_space_dir = os.path.join(
                reconst_dir, "recon_template_space"
            )
            image_3DHR = os.path.join(
                recon_template_space_dir, "srr_template.nii.gz"
            )
            image_3DHR_mask = os.path.join(
                recon_template_space_dir, "srr_template_mask.nii.gz"
            )
            image_3DHR_masked = os.path.join(
                recon_template_space_dir, "srr_template_masked_test.nii.gz"
            )
            if os.path.exists(image_3DHR):
                if not os.path.exists(image_3DHR_masked):
                    if os.path.exists(image_3DHR_mask):
                        generate_masked_volume(
                            image_3DHR_mask,
                            image_3DHR,
                            image_3DHR_masked,
                            NB_DILATION,
                        )
                    else:
                        print(f"{image_3DHR_mask} does not exist for {subject} {session}")

                else:
                    print(f"{image_3DHR_masked} already exist for {subject} {session}")
            else:
                print(f"{image_3DHR} does not exist for {subject} {session}")
