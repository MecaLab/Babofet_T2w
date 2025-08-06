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
#SBATCH --time=20:00
#SBATCH -c 1
#SBATCH --mem-per-cpu=48G
#SBATCH -e %x_%j.err
#SBATCH -o %x_%j.out

MASK_PATH="{base_path}"

OUTPUT_PATH="{dir_output_recon_template_space}"
"""
    slurm_content += "\n"
    for i, file in enumerate(masks, start=1):
        slurm_content += f"MASK_FILE{i}=\"{file}\"\n"

    mask_stacks = " ".join(["/data/$MASK_FILE{}".format(i) for i in range(1, len(masks) + 1)])

    slurm_content += f"""
singularity exec \\
    -B "$MASK_PATH":/data \\
    -B "$OUTPUT_PATH":/output \\
    /scratch/lbaptiste/softs/niftymic.multifact_latest.sif \\
    niftymic_reconstruct_volume_from_slices \\
        --filenames {mask_stacks} \\
        --dir-input-mc /output/motion_correction \\
        --output /output/srr_template_mask.nii.gz \\
        --reconstruction-space /output/srr_template.nii.gz \\
        --alpha 1 \\
        --isotropic-resolution 0.5 \\
        --mask \\
        --sda \\
"""

    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


def get_all_masks(path):
    masks = []
    for file in os.listdir(path):
        if "ND" not in file:
            if file.endswith(".nii.gz"):
                masks.append(file)
    return masks


if __name__ == "__main__":

    base_path = cfg.MESO_OUTPUT_PATH

    subject = sys.argv[1]

    input_dir = os.path.join(cfg.DATA_PATH, subject)

    for session in os.listdir(input_dir):
        subject_session_path = os.path.join(input_dir, session)

        if not "recons_rhesus" in os.listdir(subject_session_path):
            print(f"\tSkipping {subject} {session}, no recons_rhesus directory found.")
            continue

        recon_template_space_dir = os.path.join(subject_session_path, "recons_rhesus", "recon_template_space")

        if not os.path.exists(recon_template_space_dir):
            print(f"\tSkipping {subject} {session}, no recon_template_space directory found.")
            continue

        if os.path.exists(os.path.join(recon_template_space_dir, "srr_template_mask.nii.gz")):
            print(f"\tSkipping {subject} {session}, srr_template_mask.nii.gz already exists.")
            continue

        print(f"Processing {subject} {session}...")
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
