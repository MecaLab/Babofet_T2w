import os
import sys
import pandas as pd
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess
import nibabel as nib
import numpy as np

def get_gestational_info(female_name, session_id, tsv_file):
    # Atlas available timepoints
    atlas_timepoints = [85, 110, 135]

    df = pd.read_csv(tsv_file, sep='\t')

    session_data = df[df['session_id'].str.strip() == session_id]

    if session_data.empty:
        print(f"Error: Session {session_id} not found for {female_name}.")
        return None

    gestational_age = session_data['gestational_age'].values[0]

    adequate_atlas = min(atlas_timepoints, key=lambda x: abs(x - gestational_age))

    return gestational_age, adequate_atlas


def pair_data(t2w_dir, mask_dir):
    list_t2w = []
    list_masks = []

    t2w_files = [f for f in os.listdir(t2w_dir) if f.endswith("T2w_denoised.nii.gz")]

    for t2w_name in t2w_files:
        prefix = t2w_name.split("_T2w")[0]

        expected_mask_name = f"{prefix}_desc-brain_mask.nii.gz"
        mask_full_path = os.path.join(mask_dir, expected_mask_name)

        if os.path.exists(mask_full_path):
            list_t2w.append(t2w_name)
            list_masks.append(expected_mask_name)
        else:
            print(f"Warning: No matching mask found for {t2w_name} in {mask_dir}")

    return list_t2w, list_masks


def combine_brain_labels(input_path, output_path):
    # Load the segmentation mask
    img = nib.load(input_path)
    data = img.get_fdata()

    # Option 1: Combine ALL labels > 0 into 1
    # This assumes 0 is background and everything else is brain tissue
    brain_mask = np.where(data > 0, 1, 0).astype(np.uint8)

    # Option 2: Combine only SPECIFIC labels
    # labels_to_include = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # brain_mask = np.isin(data, labels_to_include).astype(np.uint8)

    # Save the new binary mask
    new_img = nib.Nifti1Image(brain_mask, img.affine, img.header)
    nib.save(new_img, output_path)


def write_slurm(
        slurm_filename,
        fullname_subj,
        stack_path,
        denoised_files,
        bm_path,
        bm_files,
        template_path,
        ga,
        soft_path):
    slurm_content = f"""#!/bin/sh
    
#SBATCH -J babofet
#SBATCH -p batch
#SBATCH -w niolon13
#SBATCH --mem-per-cpu=48G
#SBATCH --time=24:00:00
#SBATCH -N 1
#SBATCH -o logs/recon_pipeline_niftymic_{fullname_subj}.out
#SBATCH -e logs/recon_pipeline_niftymic_{fullname_subj}.err

INPUT_PATH="{stack_path}"
MASK_PATH="{bm_path}"

OUTPUT_PATH="${{INPUT_PATH}}/reconstruction_niftymic"
MOTION_CORRECTION="${{OUTPUT_PATH}}/motion_correction"

mkdir -p $OUTPUT_PATH
mkdir -p $MOTION_CORRECTION

TEMPLATE_PATH="{template_path}"
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
        -B "$TEMPLATE_PATH":/template \\
        {soft_path} \\
        niftymic_run_reconstruction_pipeline \\
            --filenames {input_stacks} \\
            --filenames-masks {mask_stacks} \\
            --dir-output /output/ \\
            --isotropic-resolution 0.5 \\
            --bias-field-correction 0 \\
            --template /template/Template_G{ga}_T2W.nii.gz \\
            --template-mask /template/Template_G{ga}_T2W_brainmask.nii.gz \\
    """

    with open(slurm_filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(slurm_filename, 0o700)

if __name__ == "__main__":
    atlas_path = cfg.FETAL_RESUS_ATLAS
    raw_path = cfg.SOURCEDATA_BIDS_PATH
    derivative_path = cfg.DERIVATIVES_BIDS_PATH
    niftymic_soft = os.path.join(cfg.SOFTS_PATH, "niftymic.multifact_latest.sif")

    slurm_dir = "slurm_files"
    if not os.path.exists(slurm_dir):
        os.makedirs(slurm_dir)

    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    subject = "sub-Aziza"
    session = "ses-02"
    fullname_subj = f"{subject}_{session}"
    slurm_filename = f"{slurm_dir}/reconstruction_niftymic_{fullname_subj}.slurm"

    tsv_file = os.path.join(raw_path, "raw", subject, f"{subject}_sessions.tsv")
    if not os.path.exists(tsv_file):
        print(f"ERROR: tsv file does not exist at {tsv_file}")
        exit()

    stacks_path = os.path.join(derivative_path, "intermediate", "niftymic", subject, session)
    if not os.path.exists(stacks_path):
        print(f"ERROR: stacks path does not exist at {stacks_path}")
        exit()

    brainmask_path = os.path.join(derivative_path, "niftymic", subject, session, "anat")
    if not os.path.exists(brainmask_path):
        print(f"ERROR: brainmask path does not exist at {brainmask_path}")
        exit()

    ga, atlas = get_gestational_info(subject, session, tsv_file)
    print(ga, atlas)
    exit()

    list_t2w, list_masks = pair_data(stacks_path, brainmask_path)

    write_slurm(
        slurm_filename=slurm_filename,
        fullname_subj=fullname_subj,
        stack_path=stacks_path,
        denoised_files=list_t2w,
        bm_path=brainmask_path,
        bm_files=list_masks,
        template_path=atlas_path,
        ga=ga,
        soft_path=niftymic_soft
    )

    print(f"\t\tComputing reconstruction for {fullname_subj}")
    subprocess.run(["sbatch", slurm_filename])