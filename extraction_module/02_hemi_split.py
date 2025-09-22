import numpy as np
import os
import sys
import ants as ants
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

# Function to adapt the atlas to the subject and compute the MI


def ants_register(fixed, moving_atlas_file, moving_atlas_mask_file=None):
    # load atlas volume
    moving_atlas = ants.image_read(moving_atlas_file)
    # fixed.plot(overlay=moving_atlas, title='Before Registration', overlay_alpha = 0.5)
    # comute registration
    if moving_atlas_mask_file is not None:
        moving_atlas_mask = ants.image_read(moving_atlas_mask_file)
        mytx = ants.registration(fixed=fixed, moving=moving_atlas, mask=moving_atlas_mask,
                                 type_of_transform="Affine")  # 'SyN' or Affine
    else:
        mytx = ants.registration(fixed=fixed, moving=moving_atlas, type_of_transform="Affine")  # 'SyN' or Affine

    gd = os.path.basename(moving_atlas_file).split("_")[1]
    ants.image_write(mytx['warpedmovout'], os.path.join(cfg.BASE_NIOLON_PATH, f"tmp_affine_{gd}.nii.gz"))
    # fwdtransforms: Transforms to move from moving to fixed image.
    # invtransforms: Transforms to move from fixed to moving image.
    # fwdtransform = mytx['fwdtransforms']
    warped_atlas = mytx['warpedmovout']
    # compute MI to find the closest atlas
    # wraped_mi = ants.image_mutual_information(fixed, warped_atlas)
    wraped_mi = ants.image_similarity(fixed, warped_atlas, metric_type="MattesMutualInformation")  # MattesMutualInformation, MeanSquares, CC, Demons
    return wraped_mi


def find_best_atlas(fixed, atlas_path, atlas_list, use_mask=True):
    best_atlas = None

    for i, atlas in enumerate(atlas_list):
        atlas_file = os.path.join(atlas_path, "Volumes", f"ONPRC_G{atlas}_Norm.nii.gz")

        if use_mask:
            mask_file = os.path.join(atlas_path, "Segmentations", f"ONPRC_G{atlas}_NFseg_bm.nii.gz")
        else:
            mask_file = None

        current_mi = ants_register(fixed, atlas_file, moving_atlas_mask_file=mask_file)
        print(f"\t\t\t{atlas}: {current_mi}")

        if best_atlas is None or current_mi < best_atlas[1]:  # < or > ?
            best_atlas = [atlas, current_mi]

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
            t2_subj_seg = os.path.join(cfg.BASE_NIOLON_PATH, "nnunet_pred_dataset_7_3000", f"{subject}_{session}.nii.gz")

            if not os.path.exists(t2_subj_seg):
                print(f"\tOriginal segmentation for {subject} {session} does not exists. Run the inference on it. Skipping...")
                continue

            fixed = ants.image_read(t2_subj)
            fixed_seg = ants.image_read(t2_subj_seg)  # np unique -> 0 1 2 3 4

            file_seg_out = os.path.join(subject_output_split_seg, f"{subject}_{session}_hemi.nii.gz")

            # find best_atlas
            best_atlas = find_best_atlas(fixed, atlas_path, atlas_timepoints, use_mask=True)
            print(f"\t\tBest altas: {best_atlas}")

            best_atlas_file = os.path.join(atlas_path, "Volumes", f"ONPRC_G{best_atlas}_Norm.nii.gz")
            moving_best_atlas = ants.image_read(best_atlas_file)

            moving_seg_file = os.path.join(atlas_path, "Segmentations", "structures_dilated", f"ONPRC_G{best_atlas}_NFseg_structures_dilated.nii.gz")

            if not os.path.exists(moving_seg_file):
                print(f"\t\tError ! File {moving_seg_file} does not exists. Run the previous script")
                continue

            moving_best_seg = ants.image_read(moving_seg_file)

            mytx_best = ants.registration(fixed=fixed, moving=moving_best_atlas, type_of_transform='SyN')  # SyN or Affine
            # fwdtransforms: Transforms to move from moving to fixed image.
            # invtransforms: Transforms to move from fixed to moving image.
            fwdtransform_best = mytx_best['fwdtransforms']
            warped_best_atlas = mytx_best['warpedmovout']

            ants.image_write(warped_best_atlas, os.path.join(cfg.BASE_NIOLON_PATH, "tmp_syn.nii.gz"))

            warped_best_seg = ants.apply_transforms(fixed=fixed, moving=moving_best_seg,
                                                    transformlist=mytx_best['fwdtransforms'],
                                                    interpolator="nearestNeighbor")

            ants.image_write(warped_best_seg, os.path.join(cfg.BASE_NIOLON_PATH, "tmp_syn_seg.nii.gz"))

            ## use the aligned atlas hemi to split the segmentation
            new_data = np.zeros_like(warped_best_seg.numpy(), dtype=np.uint8)

            new_data[(warped_best_seg.numpy() == 1) & (fixed_seg.numpy() == 1)] = 1  # CSF droit
            new_data[(warped_best_seg.numpy() == 1) & (fixed_seg.numpy() == 2)] = 2  # WM droit
            new_data[(warped_best_seg.numpy() == 1) & (fixed_seg.numpy() == 3)] = 3  # GM droit
            new_data[(warped_best_seg.numpy() == 1) & (fixed_seg.numpy() == 4)] = 4  # Ventricule droit

            new_data[(warped_best_seg.numpy() == 2) & (fixed_seg.numpy() == 1)] = 5  # CSF gauche
            new_data[(warped_best_seg.numpy() == 2) & (fixed_seg.numpy() == 2)] = 6  # WM gauche
            new_data[(warped_best_seg.numpy() == 2) & (fixed_seg.numpy() == 3)] = 7  # GM gauche
            new_data[(warped_best_seg.numpy() == 2) & (fixed_seg.numpy() == 4)] = 8  # Ventricule gauche

            new_data[(warped_best_seg.numpy() == 3)] = 9  # Tronc
            new_data[(warped_best_seg.numpy() == 4)] = 10  # Cervelet

            seg_out = fixed_seg.new_image_like(new_data)
            ants.image_write(seg_out, file_seg_out)
            print("\tSplitted segmentation saved as:", file_seg_out)

            exit()
