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
    previous_mi = None

    for i, atlas in enumerate(atlas_list):
        atlas_file = os.path.join(atlas_path, f"ONPRC_G{atlas}_Norm.nii.gz")

        current_mi = ants_register(fixed, atlas_file)
        print(f"{atlas}: {current_mi}")

        if i > 0:
            diff_mi = current_mi - previous_mi
            print(f"\t{atlas} - {atlas_list[i-1]} = {diff_mi}")

        if best_atlas is None or current_mi > best_atlas[1]:
            best_atlas = [atlas, current_mi]

        previous_mi = current_mi

    return best_atlas[0]


if __name__ == "__main__":

    recons_folder = cfg.RECONS_FOLDER
    atlas_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2")

    output_split_seg = os.path.join(atlas_path, "Seg_Hemi")

    if not os.path.exists(output_split_seg):
        os.makedirs(output_split_seg)

    for subject in os.listdir(recons_folder):
        if subject == "Aziza":
            continue
        print(f"Starting {subject}")

        subject_output_split_seg = os.path.join(output_split_seg, subject)

        if not os.path.exists(subject_output_split_seg):
            os.makedirs(subject_output_split_seg)

        subject_path = os.path.join(recons_folder, subject)
        for session in os.listdir(subject_path):
            print(f"\tSession: {session}")

            subject_sess_output_split_seg = os.path.join(subject_output_split_seg, session)

            if not os.path.exists(subject_sess_output_split_seg):
                os.makedirs(subject_sess_output_split_seg)

            session_subject_path = os.path.join(subject_path, session)

            recons_rhesus_folder = os.path.join(session_subject_path, "recons_rhesus/recon_template_space")

            t2_subj = os.path.join(recons_rhesus_folder, "srr_template.nii.gz")
            t2_subj_seg = os.path.join(cfg.BASE_NIOLON_PATH, "nnunet_pred_dataset_7_3000", f"{subject}_{session}.nii.gz")

            fixed = ants.image_read(t2_subj)
            fixed_seg = ants.image_read(t2_subj_seg)

            file_seg_out = os.path.join(subject_sess_output_split_seg, f"{subject}_{session}_hemi.nii.gz")

            # find best_atlas
            atlas_timepoints = [85, 97, 110, 122, 135, 147, 155]
            best_atlas = find_best_atlas(fixed, os.path.join(atlas_path, "Volumes"), atlas_timepoints)
            print(f"\tBest altas: {best_atlas}")

            best_atlas_file = os.path.join(atlas_path, "Volumes", f"ONPRC_G{best_atlas}_Norm.nii.gz")
            moving_best_atlas = ants.image_read(best_atlas_file)

            moving_seg_file = os.path.join(atlas_path, "Segmentations", f"ONPRC_G{best_atlas}_NFseg_3_dilall.nii.gz")

            if not os.path.exists(moving_seg_file):
                print(f"Error ! File {moving_seg_file} does not exists. Run the previous script")
                continue

            moving_best_seg = ants.image_read(moving_seg_file)

            mytx_best = ants.registration(fixed=fixed, moving=moving_best_atlas, type_of_transform='SyN')
            # fwdtransforms: Transforms to move from moving to fixed image.
            # invtransforms: Transforms to move from fixed to moving image.
            fwdtransform_best = mytx_best['fwdtransforms']
            warped_best_atlas = mytx_best['warpedmovout']
            # fixed.plot(overlay=warped_atlas,
            #           title='After Registration', overlay_alpha = 0.5)
            wraped_mi = ants.image_mutual_information(fixed, warped_best_atlas)

            warped_best_seg = ants.apply_transforms(fixed=fixed, moving=moving_best_seg,
                                                    transformlist=mytx_best['fwdtransforms'],
                                                    interpolator="nearestNeighbor")
            # ants.image_write(warped_best_atlas, aligned_image_file)
            # warpedimage.plot()
            # fixed.plot(overlay=warped_seg, title='seg on fixed', overlay_alpha=0.5)

            ## use the aligned atlas hemi to split the segmentation
            seg_arr = fixed_seg.numpy()
            bm = seg_arr > 0
            seg_atlas = warped_best_seg.numpy()
            out_arr = seg_arr + 10 * seg_atlas
            out_arr = out_arr * bm
            # recombine brainstem
            brainstem = seg_arr == 8
            out_arr[brainstem] = 8
            # recombine background
            brainstem = seg_arr == 4
            out_arr[brainstem] = 4
            seg_out = fixed_seg.new_image_like(out_arr)
            ants.image_write(seg_out, file_seg_out)
            print("\tSplitted segmentation saved as:", file_seg_out)

        exit()




