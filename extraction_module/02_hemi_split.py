import numpy as np
import os
import sys
import nibabel as nib
import ants
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def ants_register(fixed, altas_days):
    moving_atlas_file = os.path.join(cfg.FETAL_RESUS_ATLAS, f"Template_G{altas_days}_T2W.nii.gz")
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

    recons_folder = cfg.RECONS_FOLDER
    atlas_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2")


    for subject in os.listdir(recons_folder):
        if subject == "Aziza":
            continue
        print(f"Starting {subject}")

        subject_path = os.path.join(recons_folder, subject)
        for session in os.listdir(subject_path):
            print(f"\tSession: {session}")

            session_subject_path = os.path.join(subject_path, session)

            recons_rhesus_folder = os.path.join(session_subject_path, "recons_rhesus/recon_template_space")

            t2_subj = os.path.join(recons_rhesus_folder, "srr_template.nii.gz")

            # Test
            best_atlas_days = 110
            best_atlas_file = os.path.join(atlas_path, "Segmentations", "ONPRC_G110_NFseg.nii.nii.gz")
            moving_best_atlas = ants.image_read(best_atlas_file)

            moving_seg_file = os.path.join(atlas_path, "Segmentations", "ONPRC_G110_NFseg_3_dilall.nii.gz")
            moving_best_seg = ants.image_read(moving_seg_file)

            exit()




