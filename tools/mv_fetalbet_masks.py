import os
import shutil

source_folder = "/scratch/lbaptiste/data/dataset/babofet/fetalBET_masks_V2"

main_dst_folder = "/scratch/lbaptiste/data/dataset/babofet/derivatives"

for subj in os.listdir(source_folder):
    subj_path_src = os.path.join(source_folder, subj)

    subj_path_dst = os.path.join(main_dst_folder, subj)

    if not os.path.exists(subj_path_dst):
        os.makedirs(subj_path_dst)

    folder_output = os.path.join(subj_path_dst, "fetalbet_masks_v2")

    if os.path.exists(folder_output):
        print(f"Skip {subj} bc it already exists")
        continue
    else:
        os.makedirs(folder_output)

    for file in os.listdir(subj_path_src):
        if "HASTE" in file or "haste" in file:
            src_file_path = os.path.join(subj_path_src, file)
            dst_file_path = os.path.join(folder_output, file)

            shutil.copy2(src_file_path, dst_file_path)

    print(f"OK for {subj}")