import os
import sys
import pandas as pd
import argparse
import subprocess
import nibabel as nib
import numpy as np
import csv
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

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


def run_niftymic_reconstruction(fullname_subj, stack_path, denoised_files, bm_path, bm_files, template_path, ga, soft_path):
    output_path = os.path.join(stack_path, "reconstruction_niftymic")
    os.makedirs(output_path, exist_ok=True)

    if os.path.exists(os.path.join(output_path, "recon_template_space", "srr_template.nii.gz")):
        print(f"NiftyMIC reconstruction already exists for {fullname_subj}. Skipping.")
        return

    input_stacks = ["/data/" + f for f in denoised_files]
    mask_stacks = ["/masks/" + f for f in bm_files]

    # Build the command
    cmd = [
        "singularity", "exec",
        "-B", f"{stack_path}:/data",
        "-B", f"{bm_path}:/masks",
        "-B", f"{output_path}:/output",
        "-B", f"{template_path}:/template",
        soft_path,
        "niftymic_run_reconstruction_pipeline",
        "--filenames"] + input_stacks + [
        "--filenames-masks"] + mask_stacks + [
        "--dir-output", "/output/",
        "--isotropic-resolution", "0.5",
        "--bias-field-correction", "0",
        "--template", f"/template/Template_G{ga}_T2W.nii.gz",
        "--template-mask", f"/template/Template_G{ga}_T2w_brainmask.nii.gz"
    ]

    print(f"Running NiftyMIC for {fullname_subj}...")
    subprocess.run(cmd, check=True) # This waits until NiftyMIC is finished


def add_session_metadata(tsv_path, session_id, gestational_age):
    fieldnames = ['session_id', 'gestational_age']

    file_exists = os.path.isfile(tsv_path)

    with open(tsv_path, mode='a', newline='', encoding='utf-8') as tsvfile:
        writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, delimiter='\t')

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            'session_id': session_id,
            'gestational_age': gestational_age
        })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Denoise data for a specific subject and session.")
    parser.add_argument("--subject", required=True, help="Subject ID (e.g., sub-Aziza)")
    parser.add_argument("--session", required=True, help="Session ID (e.g., ses-01)")
    args = parser.parse_args()

    subject = args.subject
    session = args.session

    atlas_path = cfg.FETAL_RESUS_ATLAS
    raw_path = cfg.SOURCEDATA_BIDS_PATH
    derivative_path = cfg.DERIVATIVES_BIDS_PATH
    niftymic_soft = os.path.join(cfg.SOFTS_PATH, "niftymic.multifact_latest.sif")

    fullname_subj = f"{subject}_{session}"

    tsv_file = os.path.join(raw_path, "raw", subject, f"{subject}_sessions.tsv")
    if not os.path.exists(tsv_file):
        add_session_metadata(tsv_file, session, gestational_age=95)

    stacks_path = os.path.join(derivative_path, "intermediate", "niftymic", subject, session)
    if not os.path.exists(stacks_path):
        print(f"ERROR: stacks path does not exist at {stacks_path}")
        exit()

    brainmask_path = os.path.join(derivative_path, "niftymic", subject, session, "anat")
    if not os.path.exists(brainmask_path):
        print(f"ERROR: brainmask path does not exist at {brainmask_path}")
        exit()

    subject_ga, atlas_ga = get_gestational_info(subject, session, tsv_file)

    list_t2w, list_masks = pair_data(stacks_path, brainmask_path)

    run_niftymic_reconstruction(
        fullname_subj=fullname_subj,
        stack_path=stacks_path,
        denoised_files=list_t2w,
        bm_path=brainmask_path,
        bm_files=list_masks,
        template_path=atlas_path,
        ga=atlas_ga,
        soft_path=niftymic_soft
    )