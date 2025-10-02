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
    print("\t\tStarting registration with FLIRT")
    for moving_file in os.listdir(atlas_dir):
        if moving_file.endswith(".nii.gz") and "Norm" in moving_file:
            moving = os.path.join(atlas_dir, moving_file)

            print(f"\t\t\tProcessing {moving_file}")
            moving_name = moving_file.replace(".nii.gz", "_affine.nii.gz")
            moving_mat = moving_file.replace(".nii.gz", "_affine.mat")

            out_nii = os.path.join(output_dir, moving_name)

            if os.path.exists(out_nii):
                print(f"\t\t{moving_name} already exists, skipping...")
                continue
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


def find_best_atlas(input_atlas_registered, base_subj_path):
    reference = os.path.join(base_subj_path, "masked_template_debiased.nii.gz")
    reference_mask = os.path.join(base_subj_path, "srr_template_mask.nii.gz")

    dico_atlas_metric = {}
    for atlas_file in os.listdir(input_atlas_registered):
        if atlas_file.endswith(".nii.gz") and "affine" in atlas_file:
            atlas_path = os.path.join(input_atlas_registered, atlas_file)

            result = subprocess.run(
                [
                    "fslcc",
                    "-m", reference_mask,
                    "-p", "5",
                    reference,
                    atlas_path
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            output = result.stdout.strip()
            if output:
                fslcc_value = float(output.split()[2])
                dico_atlas_metric[atlas_file] = fslcc_value
                print(f"\t\t{atlas_file}: {fslcc_value}")

    best_atlas = max(dico_atlas_metric, key=dico_atlas_metric.get)
    return best_atlas


def convert_fsl2ants(input_atlas_registered, best_atlas, base_subj_path):
    """
    tools/c3d_affine_tool \
        -ref ${REFERENCE} \
        -src ${MOVING} \
        "$OUTPUT_DIR/affine.mat" \
        -fsl2ras \
        -oitk "$OUTPUT_DIR/affine.txt"
    """

    affine_file = os.path.join(input_atlas_registered, best_atlas.replace(".nii.gz", "_affine.mat"))
    oitk = os.path.join(input_atlas_registered, best_atlas.replace(".nii.gz", "_affine.txt"))

    subprocess.run(
        [
            "tools/c3d_affine_tool",
            "-ref", os.path.join(base_subj_path, "masked_template_debiased.nii.gz"),
            "-src", best_atlas,
            affine_file,
            "-fsl2ras",
            "-oitk", oitk
        ]
    )


def ants_nonlinear_registration(output_dir, base_subj_path, best_atlas, atlas_mask):
    ref = os.path.join(base_subj_path, "masked_template_debiased.nii.gz")
    ref_mask = os.path.join(base_subj_path, "srr_template_mask.nii.gz")

    ants_prefix = "ants_"
    ants_warped_image = "warped_IMAGE.nii.gz"

    initial_moving_transform = os.path.join(output_dir, "affine.txt")

    subprocess.run(
        [
            "antsRegistration",
            "--verbose", "1",
            "--dimensionality", "3",
            "--float", "0",
            "--output", f"[{ants_prefix}, {ants_warped_image}]",
            "--interpolation", "BSpline",
            "--use-histogram-matching", "1",
            "--winsorize-image-intensities", "[0.001,0.999]",
            "--initial-moving-transform", initial_moving_transform,
            "--transform", "SyN[0.1,3,0]",
            "--metric", f"Mattes[{ref},{best_atlas},1, 64]",
            "--convergence", "[200x200x200x200x200x200,1e-7,10]",
            "--shrink-factors", "4x4x2x2x1x1",
            "--smoothing-sigmas", "6x5x4x2x1x0",
            "--masks", f"[{ref_mask}, {atlas_mask}]",
        ],
        check=True,
        capture_output=True,
        text=True
    )




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
            subject_output_split_seg_session = os.path.join(subject_output_split_seg, session)
            if not os.path.exists(subject_output_split_seg_session):
                os.makedirs(subject_output_split_seg_session)

            recons_rhesus_folder = os.path.join(session_subject_path, "recons_rhesus/recon_template_space")

            fsl_register(volumes_atlas_path, recons_rhesus_folder, subject_output_split_seg_session)

            best_atlas = find_best_atlas(subject_output_split_seg_session, recons_rhesus_folder)

            print(f"\tBest atlas: {best_atlas}")

            best_atlas_path = os.path.join(volumes_atlas_path, best_atlas.replace("_affine.nii.gz", ".nii.gz"))

            convert_fsl2ants(subject_output_split_seg_session, best_atlas_path, recons_rhesus_folder)

            exit()