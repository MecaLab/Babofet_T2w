import subprocess
import os
import sys
import ants as ants
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def fsl_register(atlas_dir, base_subj_path, output_dir):
    reference = os.path.join(base_subj_path, "srr_template_debiased.nii.gz")
    reference_mask = os.path.join(base_subj_path, "srr_template_mask.nii.gz")
    new_reference = os.path.join(base_subj_path, "masked_template_debiased.nii.gz")

    subprocess.run(
        ["fslmaths", reference, "-mul", reference_mask, new_reference],
        check=True,
    )
    print("\tStarting registration with FLIRT")
    for moving_file in os.listdir(atlas_dir):
        if moving_file.endswith(".nii.gz") and "Norm" in moving_file:
            moving = os.path.join(atlas_dir, moving_file)

            print(f"\t\tProcessing {moving_file}")
            moving_name = moving_file.replace(".nii.gz", "_affine.nii.gz")
            moving_mat = moving_file.replace(".nii.gz", "_affine.mat")

            out_nii = os.path.join(output_dir, moving_name)
            out_mat = os.path.join(output_dir, moving_mat)

            subprocess.run(
                [
                    "flirt",
                    "-in", moving,
                    "-ref", new_reference,
                    "-out", out_nii,
                    "-omat", out_mat,
                    "-dof", "12",
                    "-cost", "mutualinfo",
                    "-searchrx", "-180", "180",
                    "-searchry", "-180", "180",
                    "-searchrz", "-180", "180",
                    "-interp", "spline"
                ],
                check=True,
            )
    print("\tFLIRT registration done")


if __name__ == "__main__":
    recons_folder = cfg.RECONS_FOLDER
    atlas_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2")

    volumes_atlas_path = os.path.join(atlas_path, "Volumes")
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
            subject_output_split_seg_session = os.path.join(subject_output_split_seg, subject, session)
            if not os.path.exists(subject_output_split_seg_session):
                os.makedirs(subject_output_split_seg_session)

            recons_rhesus_folder = os.path.join(session_subject_path, "recons_rhesus/recon_template_space")

            fsl_register(volumes_atlas_path, recons_rhesus_folder, subject_output_split_seg_session)

            exit()