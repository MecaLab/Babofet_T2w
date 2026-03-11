import os
import sys
import subprocess
import argparse
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def denoising_data_bids_format(input_path, output_path, subject, session):
    DENOISING_PATH_EXE = os.path.join(cfg.SOFTS_PATH, "DenoiseImage")

    print(f"Processing {subject} {session}")

    input_session_path = os.path.join(input_path, subject, session, "anat")
    if not os.path.exists(input_session_path):
        print(f"\t\tNo anat folder for {subject} {session}, skipping.")
        return

    output_session_path = os.path.join(output_path, subject, session)

    if not os.path.exists(output_session_path):
        os.makedirs(output_session_path)

    for file in os.listdir(input_session_path):
        if file.endswith("nii.gz"):

            input_file_path = os.path.join(input_session_path, file)

            output_filename = file.replace(".nii.gz", "_denoised.nii.gz")
            output_file_path = os.path.join(output_session_path, output_filename)
            if not os.path.exists(output_file_path):
                print(f"\t\tDenoising {file}")
                cmd = [DENOISING_PATH_EXE, "-i", input_file_path, "-o", output_file_path]
                subprocess.run(cmd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Denoise data for a specific subject and session.")
    parser.add_argument("--subject", required=True, help="Subject ID (e.g., sub-Aziza)")
    parser.add_argument("--session", required=True, help="Session ID (e.g., ses-01)")
    args = parser.parse_args()

    input_path = os.path.join(cfg.SOURCEDATA_BIDS_PATH, "raw")
    output_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "niftymic")

    denoising_data_bids_format(input_path, output_path, args.subject, args.session)
