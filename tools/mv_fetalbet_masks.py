import os
import shutil

source_folder = "/scratch/lbaptiste/data/dataset/babofet/fetalBET_masks_V2"

main_dst_folder = "scratch/lbaptiste/data/dataset/babofet/derivatives"

for subj in os.listdir(source_folder):
    subj_path_src = os.path.join(source_folder, subj)

    subj_path_dst = os.path.join(main_dst_folder, subj)

    folder_output = os.path.join(subj_path_dst, "fetalbet_masks_v2")

    if not os.path.exists(folder_output):
        os.makedirs(folder_output)

    print(folder_output, subj_path_dst)
    print(os.path.exists(folder_output), os.path.exists(subj_path_dst))

    for file in os.listdir(subj_path_src):
        if "HASTE" in file:
            file_path = os.path.join(subj_path_src, file)

            shutil.copy2(file_path, os.path.join(folder_output, file))

    print(f"OK for {subj}")
    break