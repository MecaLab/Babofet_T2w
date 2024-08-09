import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def write_slurm_file_nifty(main_path, denoised_files, bm_files, output_file):
    filename = "nifty_reconstruction.slurm"
    slurm_content = f"""#!/bin/sh
    
#SBATCH --account='a391'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=00:10:00
#SBATCH -o tmp.out
#SBATCH -e tmp.err

module load userspace/all
module load cuda/11.6

MAIN_PATH="{main_path}"

INPUT_PATH="${{MAIN_PATH}}/denoising"
MASK_PATH="${{MAIN_PATH}}/brainmask_niftymic"

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
"""

    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)

if __name__ == "__main__":
    base_path = cfg.MESO_DATA_PATH

    subject_IDs = os.listdir(base_path)
    subjects_failed = list()

    for subject in subject_IDs:
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
            bm_haste_subj_output_dir = os.path.join(subj_output_dir, "brainmask_niftymic")
            denoised_subj_output_dir = os.path.join(subj_output_dir, "denoising")
            recons_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'reconstruction_niftymic')

            if not os.path.exists(recons_haste_subj_output_dir):
                os.mkdir(recons_haste_subj_output_dir)

            anat_img = list()
            bm_img = list()
            for f in haste_files:
                filename = f.split(".")
                bm_nifti_filename = filename[0] + "_seg.nii.gz"

                anat_path_subj_path = os.path.join(denoised_subj_output_dir, f)
                bm_path_subj_path = os.path.join(bm_haste_subj_output_dir, filename[0], bm_nifti_filename)

                if os.path.exists(anat_path_subj_path) and os.path.exists(bm_path_subj_path):
                    anat_img.append(f)
                    bm_img.append(bm_nifti_filename)

            recons_haste_subj_output = os.path.join(recons_haste_subj_output_dir, subject + '_haste_3DHR.nii.gz')
            motion_subfolder = os.path.join(recons_haste_subj_output_dir, 'motion_correction')

            if os.path.exists(recons_haste_subj_output):
                print('\t\tSkipped reconstruction HASTE for {}'.format(subject))
            else:
                if not os.path.exists(motion_subfolder):
                    os.mkdir(motion_subfolder)

                recons_haste_subj_output = subject + '_haste_3DHR.nii.gz'
                write_slurm_file_nifty(
                    main_path=subj_output_dir,
                    denoised_files=anat_img,
                    bm_files=bm_img,
                    output_file=recons_haste_subj_output
                )

                exit()