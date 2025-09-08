import os
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

"""
#!/bin/bash

path_in="/envau/work/meca/users/letroter.a/MarsFet/datasets/STA_atlas_processed"
path_out="/envau/work/meca/users/letroter.a/MarsFet/datasets/STA_atlas_processed/test"

for x in {21..38}
do
echo $x

printf -v name "%02g" $x ;

brainmask="${path_in}/STA${name}_all_reg_LR_dilM.nii.gz" 
brainmask_dil="${path_out}/STA${name}_all_reg_LR_dilall.nii.gz"

fslmaths $brainmask -dilM -dilM -dilM -dilM -dilall $brainmask_dil;
fslmaths $brainmask_dil -uthr 1 $brainmask_dil;
fslmaths $brainmask_dil -dilM $brainmask_dil;
fslmaths $brainmask_dil -ero $brainmask_dil;

done
"""

if __name__ == "__main__":
    atlas_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2")

    seg_folder = os.path.join(atlas_path, "Segmentations")

    filename_in = os.path.join(seg_folder, "ONPRC_G110_NFseg_3.nii.gz")
    filename_out = os.path.join(seg_folder, f"ONPRC_G110_NFseg_3_dilall.nii.gz")

    print(f"Computing: {filename_in}")

    commands = [
        f"fslmaths {filename_in} -thr 1 -uthr 1 {seg_folder}/mask_left.nii.gz",
        f"fslmaths {filename_in} -thr 2 -uthr 2 {seg_folder}/mask_right.nii.gz",
        f"fslmaths {filename_in} -thr 3 -uthr 3 {seg_folder}/mask_cerebellum.nii.gz",
    ]

    # 2. Dilater chaque masque
    commands += [
        f"fslmaths {seg_folder}/mask_left.nii.gz -dilM {seg_folder}/mask_left_dil.nii.gz",
        f"fslmaths {seg_folder}/mask_right.nii.gz -dilM {seg_folder}/mask_right_dil.nii.gz",
        f"fslmaths {seg_folder}/mask_cerebellum.nii.gz -dilM {seg_folder}/mask_cerebellum_dil.nii.gz",
    ]

    # 3. Nettoyer chevauchements
    commands += [
        f"fslmaths {seg_folder}/mask_left_dil.nii.gz -sub {seg_folder}/mask_right_dil.nii.gz -sub {seg_folder}/mask_cerebellum_dil.nii.gz -thr 0 {seg_folder}/mask_left_clean.nii.gz",
        f"fslmaths {seg_folder}/mask_right_dil.nii.gz -sub {seg_folder}/mask_left_dil.nii.gz -sub {seg_folder}/mask_cerebellum_dil.nii.gz -thr 0 {seg_folder}/mask_right_clean.nii.gz",
        f"fslmaths {seg_folder}/mask_cerebellum_dil.nii.gz -sub {seg_folder}/mask_left_dil.nii.gz -sub {seg_folder}/mask_right_dil.nii.gz -thr 0 {seg_folder}/mask_cerebellum_clean.nii.gz",
    ]

    # 4. Recombiner en labels
    commands += [
        f"fslmaths {seg_folder}/mask_left_clean.nii.gz -mul 1 {seg_folder}/mask_left_label.nii.gz",
        f"fslmaths {seg_folder}/mask_right_clean.nii.gz -mul 2 {seg_folder}/mask_right_label.nii.gz",
        f"fslmaths {seg_folder}/mask_cerebellum_clean.nii.gz -mul 3 {seg_folder}/mask_cerebellum_label.nii.gz",
        f"fslmaths {seg_folder}/mask_left_label.nii.gz -add {seg_folder}/mask_right_label.nii.gz -add {seg_folder}/mask_cerebellum_label.nii.gz {filename_out}",
    ]

    # Exécution séquentielle
    for cmd in commands:
        print(f"Running: {cmd}")
        subprocess.run(cmd, shell=True, check=True)

    print(f"Finished! Output saved at: {filename_out}")

    """command = f"fslmaths {filename_in} -dilM -dilM -dilM -dilM -dilall {filename_out}"
    subprocess.run(command, shell=True)

    command = f"fslmaths {filename_out} -uthr 1 {filename_out}"
    subprocess.run(command, shell=True, check=True)

    command = f"fslmaths {filename_out} -dilM {filename_out}"
    subprocess.run(command, shell=True, check=True)

    command = f"fslmaths {filename_out} -ero {filename_out}"
    subprocess.run(command, shell=True)"""