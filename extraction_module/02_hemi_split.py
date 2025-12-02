import subprocess
import os
import sys
import ants as ants
import numpy as np
import shutil
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
                print(f"\t\t\t\t{moving_name} already exists, skipping...")
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
    print("\t\tFLIRT registration done")


def find_best_atlas(input_atlas_registered, base_subj_path):
    reference = os.path.join(base_subj_path, "masked_template_debiased.nii.gz")
    reference_mask = os.path.join(base_subj_path, "srr_template_mask.nii.gz")

    print("\t\tFinding best atlas with FSLCC")
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
                print(f"\t\t\t{atlas_file}: {fslcc_value}")

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

    best_atlas_name = os.path.basename(best_atlas)
    affine_file = os.path.join(input_atlas_registered, best_atlas_name.replace(".nii.gz", "_affine.mat"))
    oitk = os.path.join(input_atlas_registered, best_atlas_name.replace(".nii.gz", "_affine.txt"))

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

    print("\t\tAffine conversion done")


def ants_nonlinear_registration(input_atlas_registered, base_subj_path, best_atlas, best_atlas_mask, filename):
    ref = os.path.join(base_subj_path, "masked_template_debiased.nii.gz")
    ref_mask = os.path.join(base_subj_path, "srr_template_mask.nii.gz")

    ants_prefix = f"{input_atlas_registered}/ants_"
    ants_warped_image = filename

    best_atlas_name = os.path.basename(best_atlas)
    initial_moving_transform = os.path.join(input_atlas_registered, best_atlas_name.replace(".nii.gz", "_affine.txt"))
    full_ouput_name = f"{ants_prefix}{ants_warped_image}"

    if os.path.exists(full_ouput_name):
        print(f"\t\t{full_ouput_name} already exists, skipping...")
    else:
        subprocess.run(
        [
            "antsRegistration",
            "--verbose", "1",
            "--dimensionality", "3",
            "--float", "0",
            "--output", f"[{ants_prefix}, {full_ouput_name}]",
            "--interpolation", "BSpline",
            "--use-histogram-matching", "1",
            "--winsorize-image-intensities", "[0.001,0.999]",
            "--initial-moving-transform", initial_moving_transform,
            "--transform", "SyN[0.1,3,0]",
            "--metric", f"Mattes[{ref},{best_atlas}, 1, 64]",
            "--convergence", "[200x200x200x100x100x100, 1e-6, 10]",
            "--shrink-factors", "4x4x2x2x1x1",
            "--smoothing-sigmas", "6x5x4x2x1x0",
            "--masks", f"[{ref_mask}, {best_atlas_mask}]",
        ],
            check=True,
        )

        """shutil.move("ants_1Warp.nii.gz", os.path.join(input_atlas_registered, "ants_1Warp.nii.gz"))
        shutil.move("ants_1InverseWarp.nii.gz", os.path.join(input_atlas_registered, "ants_1InverseWarp.nii.gz"))
        try:
            full_ouput_name_tmp = full_ouput_name.replace(" ", "")
            os.rename(f" {full_ouput_name}", full_ouput_name_tmp)
            shutil.move(full_ouput_name_tmp, os.path.join(input_atlas_registered, full_ouput_name_tmp))
        except FileNotFoundError:
            shutil.move(full_ouput_name, os.path.join(input_atlas_registered, full_ouput_name))"""


def apply_ants_transformations(input_atlas_registered, base_subj_path, moving_seg, affine_file):
    ref = os.path.join(base_subj_path, "masked_template_debiased.nii.gz")

    output = os.path.join(input_atlas_registered, "warped_regionals.nii.gz")
    transform_file = os.path.join(input_atlas_registered, "ants_1Warp.nii.gz")

    subprocess.run(
        [
            "antsApplyTransforms",
            "--dimensionality", "3",
            "--input", f"{moving_seg}",
            "--reference-image", f"{ref}",
            "--output", output,
            "--transform", transform_file,
            "--transform", affine_file,
            "--interpolation", "GenericLabel",
        ],
        check=True,
    )


if __name__ == "__main__":
    recons_folder = cfg.RECONS_FOLDER
    atlas_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2")

    volumes_atlas_path = os.path.join(atlas_path, "Volumes")
    segmentation_atlas_path = os.path.join(atlas_path, "Segmentations", "structures_dilated")
    output_split_seg = os.path.join(atlas_path, "Seg_Hemi")

    if not os.path.exists(output_split_seg):
        os.makedirs(output_split_seg)

    # subjects = ["Fabienne", "Forme", "Aziza", "Filoutte", "Bibi", "Formule", "Filoutte"]
    subjects = ["Borgne"]

    for subject in os.listdir(recons_folder):
        if subject not in subjects:
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

            if not os.path.exists(recons_rhesus_folder):
                print(f"\t\trecons_rhesus folder not found for {subject} {session}, skipping...")
                continue

            file_seg_out = os.path.join(subject_output_split_seg_session, f"{subject}_{session}_hemi.nii.gz")
            if os.path.exists(file_seg_out):
                print(f"\t\tSegmentation for {subject} {session} already exists, skipping...")
                continue

            fsl_register(volumes_atlas_path, recons_rhesus_folder, subject_output_split_seg_session)

            best_atlas = find_best_atlas(subject_output_split_seg_session, recons_rhesus_folder)

            print(f"\t\tBest atlas: {best_atlas}")

            best_atlas_path = os.path.join(volumes_atlas_path, best_atlas.replace("_affine.nii.gz", ".nii.gz"))

            convert_fsl2ants(subject_output_split_seg_session, best_atlas_path, recons_rhesus_folder)

            mask_best_atlas = os.path.join(segmentation_atlas_path, best_atlas.replace("Norm_affine", "NFseg_bm"))

            filename = f"{subject}_{session}_warped_IMAGE.nii.gz"
            ants_nonlinear_registration(subject_output_split_seg_session, recons_rhesus_folder, best_atlas_path, mask_best_atlas, filename)
            subj_seg = os.path.join(segmentation_atlas_path, best_atlas.replace("Norm_affine", "structures_dilated"))

            affine_file = os.path.join(subject_output_split_seg_session, best_atlas.replace("_affine.nii.gz", "_affine.txt"))
            apply_ants_transformations(subject_output_split_seg_session, recons_rhesus_folder, subj_seg, affine_file)

            warped_best_seg = ants.image_read(os.path.join(subject_output_split_seg_session, "warped_regionals.nii.gz"))

            # CHANGE FOLDER NAME LATER !!!
            # t2_subj_seg = os.path.join(cfg.BASE_NIOLON_PATH, "segmentations_nnunet_mattia", f"{subject}_{session}.nii.gz")
            t2_subj_seg = os.path.join(cfg.BASE_NIOLON_PATH, "12_segmentations", f"{subject}_{session}.nii.gz")
            if not os.path.exists(t2_subj_seg):
                print(f"\t\tSegmentation for {subject} {session} not found, skipping...")
                continue
            fixed_seg = ants.image_read(t2_subj_seg)

            unique_label_t2 = np.unique(fixed_seg.numpy())
            if 4 in unique_label_t2:
                seg_array = fixed_seg.numpy()
                seg_array[seg_array == 4] = 2

                fixed_seg = ants.from_numpy(seg_array, origin=fixed_seg.origin, spacing=fixed_seg.spacing,
                                                direction=fixed_seg.direction)

                # ants.image_write(fixed_seg, os.path.join(cfg.BASE_NIOLON_PATH, "segmentations_nnunet_mattia", f"{subject}_{session}_corrected_3.nii.gz"))

            new_data = np.zeros_like(warped_best_seg.numpy(), dtype=np.uint8)

            new_data[(warped_best_seg.numpy() == 1) & (fixed_seg.numpy() == 1)] = 1  # CSF droit
            new_data[(warped_best_seg.numpy() == 1) & (fixed_seg.numpy() == 2)] = 2  # WM droit
            new_data[(warped_best_seg.numpy() == 1) & (fixed_seg.numpy() == 3)] = 3  # GM droit
            new_data[(warped_best_seg.numpy() == 1) & (fixed_seg.numpy() == 4)] = 2  # merge ventricule droit into wm

            new_data[(warped_best_seg.numpy() == 2) & (fixed_seg.numpy() == 1)] = 5  # CSF gauche
            new_data[(warped_best_seg.numpy() == 2) & (fixed_seg.numpy() == 2)] = 6  # WM gauche
            new_data[(warped_best_seg.numpy() == 2) & (fixed_seg.numpy() == 3)] = 7  # GM gauche
            new_data[(warped_best_seg.numpy() == 2) & (fixed_seg.numpy() == 4)] = 6  # merge Ventricule gauche into wm

            new_data[(warped_best_seg.numpy() == 3)] = 9  # Tronc
            new_data[(warped_best_seg.numpy() == 4)] = 10  # Cervelet

            seg_out = fixed_seg.new_image_like(new_data)
            ants.image_write(seg_out, file_seg_out)
            print("\tSplitted segmentation saved as:", file_seg_out)