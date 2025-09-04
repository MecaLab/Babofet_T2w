import numpy as np
import os
import sys
import nibabel as nib
import ants
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def ants_register(fixed, atlas_week):
    moving_atlas_file = os.path.join(cfg.FETAL_RESUS_ATLAS, "STA" + atlas_week + "_flipped.nii.gz")
    # load atlas volume
    moving_atlas = ants.image_read(moving_atlas_file)
    # fixed.plot(overlay=moving_atlas, title='Before Registration', overlay_alpha = 0.5)
    # comute registration
    mytx = ants.registration(fixed=fixed, moving=moving_atlas, type_of_transform="Affine")  # 'SyN' )
    # fwdtransforms: Transforms to move from moving to fixed image.
    # invtransforms: Transforms to move from fixed to moving image.
    # fwdtransform = mytx['fwdtransforms']
    warped_atlas = mytx['warpedmovout']
    # warped_atlas.plot()
    # compute MI to find the closest atlas
    wraped_mi = ants.image_mutual_information(fixed, warped_atlas)
    return wraped_mi


if __name__ == "__main__":

    volume_dir = os.path.join(cfg.BASE_NIOLON_PATH, "recons_folder")

    seg_dir_in = os.path.join(cfg.BASE_NIOLON_PATH, "nnunet_pred_dataset_7_3000")
    seg_dir_out = os.path.join(seg_dir_in, "hemi_split")

    if not os.path.exists(seg_dir_out):
        os.makedirs(seg_dir_out)

    for file in os.listdir(seg_dir_in):
        # file is Subject_sesXX.nii.gz
        file_splitted = file.split("_")  # [Subject, sesXX.nii.gz]
        subject = file_splitted[0]
        session = file_splitted[-1].split(".")[0]

        print(f"Processing {file}")

        file_seg_in = os.path.join(seg_dir_in, file)
        volume_in = os.path.join(volume_dir, subject, session, "recons_rhesus/recon_template_space/srr_template_debiased.nii.gz")

        file_seg_out = os.path.join(seg_dir_out, f"{subject}_{session}_hemi.nii.gz")

        try:
            fixed = ants.image_read(volume_in)
            fixed_seg = ants.image_read(file_seg_in)
        except Exception as e:
            print(e)

        exit()

