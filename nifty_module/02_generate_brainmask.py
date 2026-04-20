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

    input_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "niftymic")
    ouput_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "niftymic")

    # Construct the correct absolute path to the inference script
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    inference_script_path = os.path.join(current_script_dir, "fetalbet_module", "ensemble_inference.py")
    subject_path = os.path.join(input_path, subject, session)

    output_subject_path = os.path.join(ouput_path, subject, session, "anat")
    if not os.path.exists(output_subject_path):
        os.makedirs(output_subject_path)

    for file in os.listdir(subject_path):
        if file.endswith(".nii.gz") and "denoised" in file:
            image_path = os.path.join(subject_path, file)
            output_file_name = file.replace('T2w_denoised.nii.gz', 'desc-brain_mask.nii.gz')
            output_file_path = os.path.join(output_subject_path, output_file_name)

            if not os.path.exists(output_file_path):
                subprocess.run([
                    'python', inference_script_path,
                    '--image_path', image_path,
                    '--output_folder', output_file_path
                ])


