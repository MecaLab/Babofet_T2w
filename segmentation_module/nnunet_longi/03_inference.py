import os
import subprocess
import nibabel as nib
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

def prepare_t1_seg(input_folder, prepared_folder):
    for file_t in os.listdir(input_folder):
        case_name = file_t.replace("_0000.nii.gz", "")
        file_t1_path = os.path.join(input_folder, f"{case_name}_0001.nii.gz")

        image_t1 = nib.load(file_t1_path)
        data_t1 = image_t1.get_fdata()
        seg_t1 = np.zeros_like(data_t1)
        nib.save(
            nib.Nifti1Image(seg_t1, image_t1.affine, image_t1.header),
            os.path.join(prepared_folder, f"{case_name}_0002.nii.gz")
        )

    print(f"t-1 segmentations prepared. Saved in {prepared_folder}")


if __name__ == "__main__":
    dataset_id = int(sys.argv[1])
    name = sys.argv[2]
    trainer = sys.argv[3]  # "nnUNetTrainerBias_Xepochs"

    if dataset_id < 10:
        dataset_name = f"Dataset00{dataset_id}_{name}"
    elif dataset_id < 100:
        dataset_name = f"Dataset0{dataset_id}_{name}"
    else:
        dataset_name = f"Dataset{dataset_id}_{name}"

    input_folder = os.path.join(cfg.NNUNET_RAW_PATH, dataset_name, "imagesTs")

    output_folder = os.path.join(cfg.CODE_PATH, f"snapshots/nnunet_longi/pred_dataset_{dataset_id}")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    prepared_folder = os.path.join(output_folder, "prepared_t1_seg")
    if not os.path.exists(prepared_folder):
        os.makedirs(prepared_folder)
    prepare_t1_seg(input_folder, prepared_folder)

