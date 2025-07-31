import os
import sys
import json
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import shutil


def write_json_file(path, num_training, dataset_name):
    dico_data = {
        "channel_names": {
            "0": "T2W",
        },
        "labels": {
            "background": 0,
            "CSF": 1,
            "WM": 2,
            "GM": 3,
            "Ventricle": 4,
        },
        "numTraining": num_training,
        "file_ending": ".nii.gz",
        "dataset_name": dataset_name
    }
    with open(path, 'w') as f:
        json.dump(dico_data, f, indent=4)


if __name__ == "__main__":
    subject_sessions = {
        "Borgne": ["ses08", "ses09"],
        "Fabienne": ["ses03", "ses04", "ses05", "ses08"],
        "Filoutte": ["ses03", "ses04", "ses05", "ses08"],
        "Formule": ["ses02", "ses03"],
        "Bibi": ["ses07"]
    }

    mode_dataset = "debiased-2"  # "masked" or "unmasked" or "debiased-2" or "full"

    id_dataset = int(sys.argv[1])  # should be integer, eg, 1, 2, 3, etc.
    name = sys.argv[2]  # the dataset name, can be whatever you want, but you will need to use it later so remember it
    if id_dataset < 10:
        dataset_name = f"Dataset00{id_dataset}_{name}"
    elif id_dataset < 100:
        dataset_name = f"Dataset0{id_dataset}_{name}"
    else:
        dataset_name = f"Dataset{id_dataset}_{name}"

    output_path = os.path.join(cfg.NNUNET_RAW_PATH, dataset_name)

    images_tr_path = os.path.join(output_path, "imagesTr")
    images_ts_path = os.path.join(output_path, "imagesTs")
    labels_tr_path = os.path.join(output_path, "labelsTr")

    if not os.path.exists(images_tr_path):
        os.makedirs(images_tr_path)
    if not os.path.exists(images_ts_path):
        os.makedirs(images_ts_path)
    if not os.path.exists(labels_tr_path):
        os.makedirs(labels_tr_path)

    for subject, sessions in subject_sessions.items():
        print(f"Processing subject: {subject}")
        input_path_3d_segs = os.path.join(cfg.SEG_OUTPUT_PATH, subject)

        if mode_dataset == "unmasked":
            input_path_3d_stacks = os.path.join(cfg.DATA_PATH, subject)
        elif mode_dataset == "masked":
            input_path_3d_stacks = os.path.join(cfg.SEG_INPUT_PATH, subject)
        elif mode_dataset == "debiased-2":
            input_path_3d_stacks = os.path.join(cfg.DATA_PATH, subject)
        else:
            raise ValueError(f"Unknown mode_dataset: {mode_dataset}")

        for session in sessions:
            print(f"\tProcessing session: {session}")
            if mode_dataset == "unmasked":
                input_path_3d_stack = os.path.join(input_path_3d_stacks, session, "recons_rhesus/recon_template_space/srr_template_debiased.nii.gz")
            elif mode_dataset == "masked":
                input_path_3d_stack = os.path.join(input_path_3d_stacks, session, "reo-SVR-output-brain_rhesus.nii.gz")
            elif mode_dataset == "debiased-2":
                input_path_3d_stack = os.path.join(input_path_3d_stacks, session, "recons_rhesus/recon_template_space/srr_template.nii.gz")
                input_path_3d_stack_bis = os.path.join(input_path_3d_stacks, session, "recons_rhesus/recon_template_space/srr_template_debiased.nii.gz")

            input_path_3d_seg = os.path.join(input_path_3d_segs, session, "reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz")

            if mode_dataset == "debiased-2":
                output_path_3d_stack = os.path.join(images_tr_path, f"{subject}_{session}_bias_0000.nii.gz")
                output_path_3d_stack_bis = os.path.join(images_tr_path, f"{subject}_{session}_debias_0000.nii.gz")

                output_path_3d_seg = os.path.join(labels_tr_path, f"{subject}_{session}_bias.nii.gz")
                output_path_3d_seg_bis = os.path.join(labels_tr_path, f"{subject}_{session}_debias.nii.gz")

                os.system(f"cp {input_path_3d_stack} {output_path_3d_stack}")
                os.system(f"cp {input_path_3d_stack_bis} {output_path_3d_stack_bis}")

                os.system(f"cp {input_path_3d_seg} {output_path_3d_seg}")
                os.system(f"cp {input_path_3d_seg} {output_path_3d_seg_bis}")

            else:
                output_path_3d_stack = os.path.join(images_tr_path, f"{subject}_{session}_0000.nii.gz")
                output_path_3d_seg = os.path.join(labels_tr_path, f"{subject}_{session}.nii.gz")

                os.system(f"cp {input_path_3d_stack} {output_path_3d_stack}")
                os.system(f"cp {input_path_3d_seg} {output_path_3d_seg}")

    dataset_json = os.path.join(output_path, "dataset.json")
    num_training = len(os.listdir(images_tr_path))
    write_json_file(dataset_json, num_training, dataset_name)

    print("Dataset preparation completed")
    print("Now run: nnUNetv2_plan_and_preprocess -d DATASET_ID --verify_dataset_integrity")