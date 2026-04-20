import os
import sys
import argparse
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Denoise data for a specific subject and session.")
    parser.add_argument("--subject", required=True, help="Subject ID (e.g., sub-Aziza)")
    parser.add_argument("--session", required=True, help="Session ID (e.g., ses-01)")
    args = parser.parse_args()

    subject = args.subject
    session = args.session

    images_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "niftymic", subject, session)
    input_subject_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "niftymic", subject, session, "anat")

    for file in os.listdir(input_subject_path):
        if file.endswith("desc-brain_mask.nii.gz") and "haste" in file:
            print(f"\tResampling brain mask to T2 physical space using FLIRT...")

            basename_bids_ext = file.replace('desc-brain_mask.nii.gz', 'T2w_denoised.nii.gz')
            image_t2_path = os.path.join(images_path, basename_bids_ext)

            brainmask_file_path = os.path.join(input_subject_path, file)

            flirt_cmd = [
                'flirt',
                '-in', brainmask_file_path,
                '-ref', image_t2_path,
                '-out', brainmask_file_path,
                '-interp', 'nearestneighbour',
                '-applyxfm',
                '-usesqform'
            ]
            subprocess.run(flirt_cmd, check=True)

            print(f"\tCopying exact geometry from T2 to brain mask using fslcpgeom...")

            # Run fslcpgeom to ensure headers match perfectly
            fslcpgeom_cmd = [
                'fslcpgeom',
                image_t2_path,
                brainmask_file_path
            ]
            subprocess.run(fslcpgeom_cmd, check=True)