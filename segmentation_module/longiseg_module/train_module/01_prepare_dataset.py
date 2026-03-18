import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


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


def write_patients_tr(path, patients):
    with open(path, 'w') as f:
        json.dump(patients, f, indent=4)


if __name__ == "__main__":

    config_json = "segmentation_module/longiseg_module/config.json"
    with open(config_json, "r") as file:
        data = json.load(file)

    train_subject_sessions = data["train_subject_sessions"]
    test_subject_sessions = data["test_subject_sessions"]

    seg_dataset = os.path.join(cfg.BASE_PATH, "gt_dataset_2")

    id_dataset = int(sys.argv[1])  # should be integer, eg, 1, 2, 3, etc.
    name = sys.argv[2]  # the dataset name, can be whatever you want, but you will need to use it later so remember it

    dataset_name = f"Dataset{id_dataset:03d}_{name}"

    output_path = os.path.join(cfg.LONGISEG_RAW_PATH_MESO, dataset_name)

    images_tr_path = os.path.join(output_path, "imagesTr")
    images_ts_path = os.path.join(output_path, "imagesTs")
    labels_tr_path = os.path.join(output_path, "labelsTr")

    if not os.path.exists(images_tr_path):
        os.makedirs(images_tr_path)
    if not os.path.exists(images_ts_path):
        os.makedirs(images_ts_path)
    if not os.path.exists(labels_tr_path):
        os.makedirs(labels_tr_path)

    dico_subj = {}

    print("Training files...")
    for subject, sessions in train_subject_sessions.items():
        print(f"\tProcessing subject: {subject}")
        input_path_3d_segs = os.path.join(cfg.BASE_PATH, seg_dataset, "train_dataset")

        input_path_3d_stacks = os.path.join(cfg.DATA_PATH, subject)

        dico_subj[subject] = []

        for session in sessions:
            print(f"\t\tProcessing session: {session}")

            dico_subj[subject].append(f"{subject}_{session}")

            input_path_3d_stack = os.path.join(input_path_3d_stacks, session, "recons_rhesus/recon_template_space/srr_template.nii.gz")
            input_path_3d_seg = os.path.join(input_path_3d_segs, f"{subject}_{session}.nii.gz")

            output_path_3d_stack = os.path.join(images_tr_path, f"{subject}_{session}_0000.nii.gz")
            output_path_3d_seg = os.path.join(labels_tr_path, f"{subject}_{session}.nii.gz")

            os.system(f"cp {input_path_3d_stack} {output_path_3d_stack}")
            os.system(f"cp {input_path_3d_seg} {output_path_3d_seg}")

    print("Testing files...")
    for subject, sessions in test_subject_sessions.items():
        print(f"\tProcessing subject: {subject}")
        input_path_3d_segs = os.path.join(cfg.BASE_PATH, seg_dataset, "test_dataset")

        input_path_3d_stacks = os.path.join(cfg.DATA_PATH, subject)

        for session in sessions:
            print(f"\t\tProcessing session: {session}")

            # dico_subj[subject].append(f"{subject}_{session}")

            input_path_3d_stack = os.path.join(input_path_3d_stacks, session, "recons_rhesus/recon_template_space/srr_template.nii.gz")

            output_path_3d_stack = os.path.join(images_ts_path, f"{subject}_{session}_0000.nii.gz")

            os.system(f"cp {input_path_3d_stack} {output_path_3d_stack}")


    dataset_json = os.path.join(output_path, "dataset.json")
    patients_tr_json = os.path.join(output_path, "patientsTr.json")

    num_training = len(os.listdir(labels_tr_path))
    write_json_file(dataset_json, num_training, dataset_name)
    write_patients_tr(patients_tr_json, dico_subj)

    print("Dataset preparation completed")
    print("Running dataset check...")
    # os.system(f"nnUNetv2_plan_and_preprocess -d {id_dataset} --verify_dataset_integrity")