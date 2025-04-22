"""Generate a masked v
TODO: create a slurm version of this python script
"""

import os

import numpy as np
import nibabel as nib
from skimage import morphology as smo


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
    DB = "/scratch/apron/data/datasets/MarsFet/derivatives"
    input_DB_path = os.path.join(DB, "brain_seg")
    # path for writing output
    output_DB_path = os.path.join(DB, "srr_reconstruction", "default_pipeline_meso")

    sequences = ["haste", "tru"]

    subjects = os.listdir(output_DB_path)
    subjects.sort()
    for subject in subjects[:10]:
        subj_dir = os.path.join(output_DB_path, subject)
        sessions = os.listdir(subj_dir)
        for session in sessions:
            session_dir = os.path.join(subj_dir, session)
            for sequence in sequences:
                reconst_dir = os.path.join(session_dir, sequence)
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
                            print(
                                f"Input 3D template mask of {subject}_"
                                f"{session}_acq-{sequence} "
                                f"does not exist"
                            )

                    else:
                        print(
                            f" 3D masked template volume of {subject}_"
                            f"{session}_acq-{sequence} "
                            f" already exist"
                        )
                else:
                    print(
                        f"Input 3D template  volume of {subject}_"
                        f"{session}_acq-{sequence} does not exist"
                    )
