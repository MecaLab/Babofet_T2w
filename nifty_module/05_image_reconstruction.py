import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess


def write_slurm_file_nifty(subj, main_path, denoised_files, bm_folder, bm_files, output_file, mode_bm="manual", suffix=""):
    filename = "nifty_reconstruction.slurm"
    slurm_content = f"""#!/bin/sh
    
#SBATCH --account='b219'
#SBATCH --partition=volta
#SBATCH --time=6:00:00
#SBATCH --gres=gpu:1
#SBATCH -c 1
#SBATCH --mem-per-cpu=50G
#SBATCH -o recon_niftymic_{subj}.out
#SBATCH -e recon_niftymic_{subj}.err

module purge
module load userspace/all
module load cuda/10.2

MAIN_PATH="{main_path}"

INPUT_PATH="${{MAIN_PATH}}/denoising"
MASK_PATH="${{MAIN_PATH}}/{bm_folder}"

OUTPUT_PATH="${{MAIN_PATH}}/haste/reconstruction_niftymic"
MOTION_CORRECTION="${{OUTPUT_PATH}}/motion_correction"
OUTPUT_FILE="{output_file}"
"""

    slurm_content += "\n"
    for i, file in enumerate(denoised_files, start=1):
        slurm_content += f"INPUT_FILE{i}=\"{file}\"\n"

    slurm_content += "\n"

    for i, file in enumerate(bm_files, start=1):
        slurm_content += f"MASK_FILE{i}=\"{file}\"\n"

    input_stacks = " ".join(["/data/$INPUT_FILE{}".format(i) for i in range(1, len(denoised_files) + 1)])
    mask_stacks = " ".join(["/masks/$MASK_FILE{}".format(i) for i in range(1, len(bm_files) + 1)])

    slurm_content += f"""
singularity exec \\
    -B "$INPUT_PATH":/data \\
    -B "$MASK_PATH":/masks \\
    -B "$OUTPUT_PATH":/output \\
    /scratch/lbaptiste/softs/niftymic.multifact_latest.sif \\
    niftymic_reconstruct_volume \\
        --filenames {input_stacks} \\
        --filenames-masks {mask_stacks} \\
        --output /output/$OUTPUT_FILE \\
        --isotropic-resolution 0.4 \\
        
./mv_recons.sh {subj} {mode_bm} {suffix}
"""

    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


"""
Parametres:
-- bias-field-correction Turn on/off bias field correction step during data preprocessing (default: 0)
-- two-step-cycle: Changer le nombre de cycle (défault 3)
-- threshold(-first): est utilisé pour rejeter les slices (NCC). -first pour le premier cycle, rien pour le cycle au milieu (moyenne des 2)
"""


if __name__ == "__main__":
    base_path = cfg.MESO_DATA_PATH

    subject_IDs = os.listdir(base_path)

    # /!\ When changing this value, make sur to update the 2nd parameter of mv_recons.sh file within the slurm file
    mask_model = "manual"  # could be 'nifty' or 'mattia' or 'manual'

    if mask_model == "manual":
        bm_folder = "manual_masks"
    elif mask_model == "nifty":
        bm_folder = "brainmask_niftymic"
    elif mask_model == "mattia":
        bm_folder = "mattia_masks"

    SUFFIX_EXP = ""  # need to be updated for every exp

    list_subjs = [
        # "sub-Fabienne_ses-09",
        "sub-Aziza_ses-05",  # "sub-Aziza_ses-05", "sub-Aziza_ses-09",
        # "sub-Formule_ses-01", "sub-Formule_ses-05", "sub-Formule_ses-09",
    ]

    for subject in subject_IDs:
        if subject not in list_subjs:
            # print(f"Skip {subject}\n")
            continue

        subj_output_dir = os.path.join(cfg.MESO_OUTPUT_PATH, subject)

        if not os.path.exists(subj_output_dir):
            os.makedirs(subj_output_dir)

        print("Starting {}".format(subject))

        dir_list = os.listdir(os.path.join(subj_output_dir, "denoising"))
        haste_files = list()
        truefisp_files = list()

        for d in dir_list:
            d_lower = d.lower()
            if "haste" in d_lower:
                haste_files.append(d)
            if "trufi" in d_lower:
                truefisp_files.append(d)

        if len(haste_files) > 0:
            print("\tStarting HASTE {}".format(subject))
            haste_subj_output_dir = os.path.join(subj_output_dir, "haste")
            bm_haste_subj_output_dir = os.path.join(subj_output_dir, bm_folder)

            denoised_subj_output_dir = os.path.join(subj_output_dir, "denoising")
            recons_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'reconstruction_niftymic')

            if not os.path.exists(recons_haste_subj_output_dir):
                os.mkdir(recons_haste_subj_output_dir)

            anat_img = list()
            bm_img = list()
            for f in haste_files:
                filename = f.split(".")
                anat_path_subj_path = os.path.join(denoised_subj_output_dir, f)
                if mask_model == "nifty":  # for brainmask_niftymic folder
                    bm_nifti_filename = filename[0] + "_seg.nii.gz"
                    bm_path_subj_path = os.path.join(bm_haste_subj_output_dir, filename[0], bm_nifti_filename)

                elif mask_model == "manual":  # with manual brainmask
                    bm_nifti_filename = filename[0] + "_mask.nii"
                    bm_path_subj_path = os.path.join(bm_haste_subj_output_dir, bm_nifti_filename)
                    if not os.path.exists(bm_path_subj_path):
                        bm_nifti_filename = filename[0] + "_mask.nii.gz"
                        bm_path_subj_path = os.path.join(bm_haste_subj_output_dir, bm_nifti_filename)

                elif mask_model == "mattia":  # with mattia brainmask
                    bm_nifti_filename = filename[0] + "_mask.nii.gz"
                    bm_path_subj_path = os.path.join(bm_haste_subj_output_dir, bm_nifti_filename)

                if os.path.exists(anat_path_subj_path) and os.path.exists(bm_path_subj_path):
                    anat_img.append(f)
                    bm_img.append(bm_nifti_filename)

            motion_subfolder = os.path.join(recons_haste_subj_output_dir, 'motion_correction')

            if not os.path.exists(motion_subfolder):
                os.mkdir(motion_subfolder)

            recons_haste_subj_output = subject + f"_haste_3DHR_{mask_model}_bm{SUFFIX_EXP}_pipeline.nii.gz"

            write_slurm_file_nifty(
                subj=subject,
                main_path=subj_output_dir,
                denoised_files=anat_img,
                bm_folder=bm_folder,
                bm_files=bm_img,
                output_file=recons_haste_subj_output,
                mode_bm=mask_model,
                suffix=SUFFIX_EXP,
            )

            # subprocess.run(["sbatch", "nifty_reconstruction.slurm"])
            print(f"\t\tComputing reconstruction for {subject}\n")