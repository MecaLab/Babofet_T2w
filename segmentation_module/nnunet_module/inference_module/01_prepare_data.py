import os
import shutil
import json
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

def format_session_str(sess):
    id_sess = sess[3:]
    return f"ses-{id_sess}"


if __name__ == "__main__":
    config_json = "segmentation_module/nnunet_module/config.json"
    with open(config_json, "r") as file:
        data = json.load(file)

    inference_data = data["inference_subject_sessions"]

    input_base_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "niftymic")
    output_base_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "nnunet", "inference_dataset")

    if not os.path.exists(output_base_path):
        os.makedirs(output_base_path)

    for subject, sessions in inference_data.items():
        print(f"Processing subject: {subject}")
        input_path_3d_stacks = os.path.join(input_base_path, subject)

        for session in sessions:
            session_formatted = format_session_str(session)
            print(f"\tProcessing session: {session_formatted}")

            input_path_3d_stack = os.path.join(input_path_3d_stacks, session_formatted, "reconstruction_niftymic",
                                               "recon_template_space", "srr_template.nii.gz")
            output_path_3d_stack = os.path.join(output_base_path, f"{subject}_{session}_0000.nii.gz")
            shutil.copy(input_path_3d_stack, output_path_3d_stack)


