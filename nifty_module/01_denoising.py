import os
import sys
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def denoising_data_bids_format(input_path, output_path):
    DENOISING_PATH_EXE = os.path.join(cfg.SOFTS_PATH, "DenoiseImage")

    for folder in os.listdir(input_path):
        if folder.startswith("sub"):
            print(f"Processing {folder}")

            input_folder_path = os.path.join(input_path, folder)
            for session in os.listdir(input_folder_path):
                if session.startswith("ses"):
                    print(f"\t{session}")

                    input_session_path = os.path.join(input_folder_path, session, "anat")
                    output_session_path = os.path.join(output_path, folder, session)

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

    input_path = os.path.join(cfg.SOURCEDATA_BIDS_PATH, "raw")
    output_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "niftymic")

    denoising_data_bids_format(input_path, output_path)