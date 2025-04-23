import os
import glob
import sys
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def write_slurm_file(base_path, masks, dir_output_recon_template_space):
    filename = "slurm_files/niftymic_reconstruct_3D_mask.slurm"

    slurm_content = f"""#!/bin/sh

#SBATCH --account='b219'
#SBATCH --partition=skylake
#SBATCH --time=4:00:00
#SBATCH -c 1
#SBATCH --mem-per-cpu=48G
#SBATCH -e %x_%j.err
#SBATCH -o %x_%j.out

MASK_PATH="{base_path}"

OUTPUT_PATH="{dir_output_recon_template_space}"
"""
    slurm_content += "\n"
    for i, file in enumerate(masks, start=1):
        slurm_content += f"$MASK_FILE{i}=\"{file}\"\n"

    mask_stacks = " ".join(["/data/$MASK_FILE{}".format(i) for i in range(1, len(masks) + 1)])

    slurm_content += f"""
singularity exec \\
    -B "$MASK_PATH":/data \\
    -B "$OUTPUT_PATH":/output \\
    /scratch/lbaptiste/softs/niftymic.multifact_latest.sif \\
    niftymic_reconstruct_volume_from_slices \\
        --filenames {mask_stacks} --dir-input-mc /output/motion_correction --output /output/srr_template_mask.nii.gz --reconstruction-space /output/srr_template.nii.gz --alpha 1 --isotropic-resolution 0.5 --mask --sda
"""

    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)

"""
singularity run -B /scratch/lbaptiste/data/dataset/babofet/derivatives/sub-Aziza_ses-05/fetalbet_masks_v2/:/data -B /scratch/lbaptiste/data/recons_folder/Aziza/ses05/recons_pipeline/recon_template_space/:/output ../softs/niftymic.multifact_latest.sif
    niftymic_reconstruct_volume_from_slices --filenames /data/sub-Aziza_ses-05_T2_HASTE_AX2_11_denoised_mask.nii.gz /data/sub-Aziza_ses-05_T2_HASTE_AX_8_denoised_mask.nii.gz /data/sub-Aziza_ses-05_T2_HASTE_COR_10_denoised_mask.nii.gz /data/sub-Aziza_ses-05_T2_HASTE_COR_13_denoised_mask.nii.gz /data/sub-Aziza_ses-05_T2_HASTE_SAG2_12_denoised_mask.nii.gz /data/sub-Aziza_ses-05_T2_HASTE_SAG_9_denoised_mask.nii.gz --output /output/srr_template_mask.nii.gz --dir-input-mc /output/motion_correction/ --reconstruction-space /output/srr_template.nii.gz --isotropic-resolution 0.5 --alpha 1 --sda --mask
"""

def brainmask_reconstruction(masks, dir_output_recon_template_space):

    image_3DHR = os.path.join(dir_output_recon_template_space, "srr_template.nii.gz")
    image_3DHR_mask = os.path.join(
        dir_output_recon_template_space, "srr_template_mask.nii.gz"
    )
    dir_motion_correction = os.path.join(
        dir_output_recon_template_space, "motion_correction"
    )
    cmd = "niftymic_reconstruct_volume_from_slices"
    cmd += " "
    cmd += "--filenames "
    for m in masks:
        cmd += m + " "
    cmd += "--dir-input-mc "
    cmd += dir_motion_correction
    cmd += " "
    cmd += "--output "
    cmd += image_3DHR_mask
    cmd += " "
    cmd += "--reconstruction-space"
    cmd += " "
    cmd += image_3DHR
    cmd += " "
    cmd += "--log-config 1"
    cmd += " "
    cmd += "--mask"
    cmd += " "
    cmd += "--isotropic-resolution 0.5"
    cmd += " "
    cmd += "--sda"
    cmd += " "
    cmd += "--alpha 1"
    return cmd


def get_all_masks(path):
    masks = []
    for file in os.listdir(path):
        if "ND" not in file:
            if file.endswith(".nii.gz"):
                masks.append(file)
    return masks


if __name__ == "__main__":

    base_path = cfg.MESO_OUTPUT_PATH

    input_dir = cfg.DATA_PATH

    for subject in os.listdir(input_dir):
        subject_path = os.path.join(input_dir, subject)
        for session in os.listdir(subject_path):
            subject_session_path = os.path.join(subject_path, session)

            if not "recons_pipeline" in os.listdir(subject_session_path):
                continue

            print(f"Processing {subject} {session}...")

            recon_template_space_dir = os.path.join(subject_session_path, "recons_pipeline", "recon_template_space")

            subj_session_path = f"sub-{subject}_ses-{session[3:]}"
            subj_derivatives_path = os.path.join(base_path, subj_session_path, "fetalbet_masks_v2")
            masks = get_all_masks(subj_derivatives_path)

            dir_motion_correction = os.path.join(recon_template_space_dir, "motion_correction")
            files_dir_motion_correction = glob.glob(os.path.join(dir_motion_correction, "*.tfm"))

            for dn_f in files_dir_motion_correction:
                if "_denoised" in dn_f:
                    bm_file = dn_f.replace("_denoised", "")
                    os.system("cp " + dn_f + " " + bm_file)

            write_slurm_file(subj_derivatives_path, masks, recon_template_space_dir)

            subprocess.run(["sbatch", "slurm_files/niftymic_reconstruct_3D_mask.slurm"])
            exit()

    """
    # path for images HASTE et TRUEFISP
    DB = "/scratch/apron/data/datasets/MarsFet/derivatives"
    input_DB_path = os.path.join(DB, "preprocessing")
    # path for writing output
    output_DB_path = os.path.join(DB, "srr_reconstruction", "default_pipeline_meso")
    sequences = ["haste"]

    subjects = os.listdir(output_DB_path)
    for subject in subjects:
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
                    recon_template_space_dir, "srr_template_masked.nii.gz"
                )
                if os.path.exists(image_3DHR):
                    if not os.path.exists(image_3DHR_masked):

                        # Get all original masks
                        masks = glob.glob(
                            os.path.join(
                                input_DB_path, subject, session, sequence, "*.nii.gz",
                            )
                        )
                        print("toto", masks)
                        sing_masks = [m.replace(DB, "/data") for m in masks]

                        # Retrieve affine transformation for correction
                        dir_motion_correction = os.path.join(
                            recon_template_space_dir, "motion_correction"
                        )
                        files_dir_motion_correction = glob.glob(
                            os.path.join(dir_motion_correction, "*.tfm")
                        )

                        for dn_f in files_dir_motion_correction:
                            bm_file = dn_f.replace("_denoised", "")
                            os.system("cp " + dn_f + " " + bm_file)

                        sing_recon_template = recon_template_space_dir.replace(
                            DB, "/data"
                        )

                        cmd_os = brainmask_reconstruction(
                            sing_masks, sing_recon_template,
                        )

                        cmd = (
                            "sbatch"
                            + "  "
                            + "/scratch/apron/code/marsFet_management/marsFet/utils/slurm/nifty_mic_singularity.slurm"
                            + " "
                            + '"'
                            + cmd_os
                            + '"'
                            + " "
                            + DB
                        )
                        os.system(cmd)
                    else:
                        print("3D masked data already exists")
                else:
                    print("Input 3D template data does not exist")
    """