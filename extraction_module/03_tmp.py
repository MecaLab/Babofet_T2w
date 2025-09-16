import numpy as np
import os
import sys
import nibabel as nib
import ants
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def ants_register(fixed, moving_atlas_file):
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


def find_best_atlas(fixed, atlas_path, atlas_list):
    best_atlas = None

    for i, atlas in enumerate(atlas_list):
        atlas_file = os.path.join(atlas_path, f"ONPRC_G{atlas}_Norm.nii.gz")

        current_mi = ants_register(fixed, atlas_file)
        print(f"\t{atlas}: {current_mi}")

        if i > 0:
            diff_mi = current_mi - previous_mi
            print(f"\t\t{atlas} - {atlas_list[i-1]} = {diff_mi}")

        if best_atlas is None or current_mi > best_atlas[1]:  # < or > ?
            best_atlas = [atlas, current_mi]

        previous_mi = current_mi

    return best_atlas[0]


if __name__ == "__main__":
    recons_folder = cfg.RECONS_FOLDER
    atlas_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2")

    output_split_seg = os.path.join(atlas_path, "Seg_Hemi")

    atlas_timepoints = [85, 97, 110, 122, 135, 147, 155]

    if not os.path.exists(output_split_seg):
        os.makedirs(output_split_seg)

    for subject in os.listdir(recons_folder):
        if subject != "Borgne":
            continue
        print(f"Starting {subject}")

        subject_output_split_seg = os.path.join(output_split_seg, subject)

        if not os.path.exists(subject_output_split_seg):
            os.makedirs(subject_output_split_seg)

        subject_path = os.path.join(recons_folder, subject)
        for session in os.listdir(subject_path):
            print(f"\tSession: {session}")

            session_subject_path = os.path.join(subject_path, session)

            recons_rhesus_folder = os.path.join(session_subject_path, "recons_rhesus/recon_template_space")

            t2_subj = os.path.join(recons_rhesus_folder, "srr_template_debiased.nii.gz")
            t2_subj_seg = os.path.join(cfg.BASE_NIOLON_PATH, "nnunet_pred_dataset_7_3000",
                                       f"{subject}_{session}.nii.gz")

            if not os.path.exists(t2_subj_seg):
                print(
                    f"\tOriginal segmentation for {subject} {session} does not exists. Run the inference on it. Skipping...")
                continue

            fixed = ants.image_read(t2_subj)
            fixed_seg = ants.image_read(t2_subj_seg)

            file_seg_out = os.path.join(subject_output_split_seg, f"{subject}_{session}_hemi.nii.gz")

            # find best_atlas
            best_atlas = find_best_atlas(fixed, os.path.join(atlas_path, "Volumes"), atlas_timepoints)
            print(f"\tBest altas: {best_atlas}")

            moving_seg_file = os.path.join(atlas_path, "Segmentations", "structures_dilated", f"ONPRC_G{best_atlas}_NFseg_structures_dilated.nii.gz")

            hemi_splitted_seg = nib.load(moving_seg_file)
            nnunet_seg = nib.load(t2_subj_seg)

            hemi_data = hemi_splitted_seg.get_fdata()
            tissue_data = nnunet_seg.get_fdata()

            new_data = np.zeros_like(tissue_data, dtype=np.uint8)

            # Règles de mapping
            # Hémisphère gauche (label 2 dans hemi_data)
            new_data[(hemi_data == 2) & (tissue_data == 1)] = 1  # CSF gauche
            new_data[(hemi_data == 2) & (tissue_data == 2)] = 2  # WM gauche
            new_data[(hemi_data == 2) & (tissue_data == 3)] = 3  # GM gauche
            new_data[(hemi_data == 2) & (tissue_data == 4)] = 4  # Ventricule gauche

            # Hémisphère droit (label 1 dans hemi_data)
            new_data[(hemi_data == 1) & (tissue_data == 1)] = 5  # CSF droit
            new_data[(hemi_data == 1) & (tissue_data == 2)] = 6  # WM droit
            new_data[(hemi_data == 1) & (tissue_data == 3)] = 7  # GM droit
            new_data[(hemi_data == 1) & (tissue_data == 4)] = 8  # Ventricule droit

            # Cervelet (label 3 dans hemi_data)
            new_data[(hemi_data == 3)] = 9

            # Tronc cérébral (label 4 dans hemi_data)
            new_data[(hemi_data == 4)] = 10

            # Sauvegarder
            output_img = nib.Nifti1Image(new_data, hemi_splitted_seg.affine, hemi_splitted_seg.header)
            nib.save(output_img, file_seg_out)
