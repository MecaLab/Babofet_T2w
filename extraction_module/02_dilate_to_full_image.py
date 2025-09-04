import os
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

base_path = "/envau/work/meca/data/babofet_DB/2024_new_stuff/nnunet_pred_dataset_7_3000/"
path_in = os.path.join(base_path, "brainmask")
path_out = os.path.join(base_path, "dilatation")

if not os.path.exists(path_out):
    os.makedirs(path_out)

for file in os.listdir(path_in):
    if file.endswith(".nii.gz"):
        print(f"Processing {file}")

        full_path_in = os.path.join(path_in, file)
        full_path_out = os.path.join(path_out, f"dil_{file}")

        command = f"fslmaths {full_path_in} -dilM -dilM -dilM -dilM -dilall {full_path_out}"
        subprocess.run(command, shell=True)

        command = f"fslmaths {full_path_out} -uthr 1 {full_path_out}"
        subprocess.run(command, shell=True)

        command = f"fslmaths {full_path_out} -dilM {full_path_out}"
        subprocess.run(command, shell=True)

        command = f"fslmaths {full_path_out} -ero {full_path_out}"
        subprocess.run(command, shell=True)

        print("Fin")
        exit()
