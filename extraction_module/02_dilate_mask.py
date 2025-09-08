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

    command = f"fslmaths {filename_in} -dilM -dilM -dilM -dilM -dilall {filename_out}"
    subprocess.run(command, shell=True)

    command = f"fslmaths {filename_out} -uthr 1 {filename_out}"
    subprocess.run(command, shell=True, check=True)

    command = f"fslmaths {filename_out} -ero {filename_out}"
    subprocess.run(command, shell=True)