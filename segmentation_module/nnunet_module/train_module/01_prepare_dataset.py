import os
import shutil
import sys
import json
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def format_session_str(sess):
    id_sess = sess[3:]
    return f"ses-{id_sess}"


def write_json_file(path, num_training, dataset_name, use_debias=False):
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
    if use_debias:
        dico_data["channel_names"] = {
            "0": "T2W",
            "1": "T2W",
        }

    with open(path, 'w') as f:
        json.dump(dico_data, f, indent=4)


if __name__ == "__main__":
    """
    Je viens de me rendre compte que preparer le dataset n'est utile que pour l'entrainement
    Ce scritp a été modifé pour être adapté sur niolon, mais ça ne sert à rien car l'entrainement se fait sur le meso
    A revenir ici plus tard
    """

    base_path = cfg.DERIVATIVES_BIDS_PATH
    input_base_path = os.path.join(base_path, "intermediate", "niftymic")

    if not os.path.exists(input_base_path):
        raise FileNotFoundError(f"Input base path does not exist: {input_base_path}")

    output_base_path = os.path.join(base_path, "intermediate", "nnunet")

    if not os.path.exists(output_base_path):
        os.makedirs(output_base_path)

    config_json = "segmentation_module/nnunet_module/config.json"
    with open(config_json, "r") as file:
        data = json.load(file)

    train_subject_sessions = data["train_subject_sessions"]
    test_subject_sessions = data["test_subject_sessions"]

    seg_dataset = os.path.join(cfg.BASE_NIOLON_PATH, "gt_dataset")

    id_dataset = int(sys.argv[1])  # should be integer, eg, 1, 2, 3, etc.
    name = sys.argv[2]  # the dataset name, can be whatever you want, but you will need to use it later so remember it
    use_debias = sys.argv[3].lower() == 'true'  # whether to use debiasing or not

    dataset_name = f"Dataset{id_dataset:03d}_{name}"

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


    print("Training files...")
    for subject, sessions in train_subject_sessions.items():
        print(f"\tProcessing subject: {subject}")
        input_path_3d_segs = os.path.join(seg_dataset, "train_dataset")
        input_path_3d_stacks = os.path.join(input_base_path, subject)

        for session in sessions:
            session_formatted = format_session_str(session)
            print(f"\t\tProcessing session: {session_formatted}")

            input_path_3d_stack = os.path.join(input_path_3d_stacks, session_formatted, "reconstruction_niftymic",
                                               "recon_template_space", "srr_template.nii.gz")
            input_path_3d_seg = os.path.join(input_path_3d_segs, f"{subject}_{session}.nii.gz")

            output_path_3d_stack = os.path.join(images_tr_path, f"{subject}_{session}_0000.nii.gz")
            output_path_3d_seg = os.path.join(labels_tr_path, f"{subject}_{session}.nii.gz")

            shutil.copy(input_path_3d_stack, output_path_3d_stack)
            shutil.copy(input_path_3d_seg, output_path_3d_seg)

            if use_debias:
                input_path_3d_stack_bis = os.path.join(input_path_3d_stacks, session_formatted,
                                                       "reconstruction_niftymic", "recon_template_space",
                                                       "srr_template_debiased.nii.gz")
                output_path_3d_stack_bis = os.path.join(images_tr_path, f"{subject}_{session}_0001.nii.gz")

                shutil.copy(input_path_3d_stack_bis, output_path_3d_stack_bis)

    print("Testing files...")
    for subject, sessions in test_subject_sessions.items():
        print(f"\tProcessing subject: {subject}")
        input_path_3d_segs = os.path.join(seg_dataset, "test_dataset")

        input_path_3d_stacks = os.path.join(input_base_path, subject)

        for session in sessions:
            session_formatted = format_session_str(session)
            print(f"\t\tProcessing session: {session_formatted}")

            input_path_3d_stack = os.path.join(input_path_3d_stacks, session_formatted, "reconstruction_niftymic",
                                               "recon_template_space", "srr_template.nii.gz")

            output_path_3d_stack = os.path.join(images_ts_path, f"{subject}_{session}_0000.nii.gz")

            shutil.copy(input_path_3d_stack, output_path_3d_stack)

            if use_debias:
                input_path_3d_stack_bis = os.path.join(input_path_3d_stacks, session_formatted,
                                                       "reconstruction_niftymic", "recon_template_space",
                                                       "srr_template_debiased.nii.gz")
                output_path_3d_stack_bis = os.path.join(images_ts_path, f"{subject}_{session}_0001.nii.gz")

                shutil.copy(input_path_3d_stack_bis, output_path_3d_stack_bis)

    dataset_json = os.path.join(output_path, "dataset.json")
    num_training = len(os.listdir(labels_tr_path))
    write_json_file(dataset_json, num_training, dataset_name, use_debias)

    print("Dataset preparation completed")
    print("Running dataset check...")
    # os.system(f"nnUNetv2_plan_and_preprocess -d {id_dataset} --verify_dataset_integrity")