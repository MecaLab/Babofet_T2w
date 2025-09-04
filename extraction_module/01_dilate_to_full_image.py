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
    atlas_path = cfg.ATLAS_GHOLIPOUR_PATH

    for file in os.listdir(atlas_path):
        if "all_reg_LR_dilM" in file:
            print(f"Processing {file}")

            full_path_in = os.path.join(atlas_path, file)
            filename_output = file.replace("all_reg_LR_dilM", "all_reg_LR_dilall")
            full_path_out = os.path.join(atlas_path, filename_output)

            command = f"fslmaths {full_path_in} -dilM -dilM -dilM -dilM {full_path_out}"
            subprocess.run(command, shell=True)

            command = f"fslmaths {full_path_out} -uthr 1 {full_path_out}"
            subprocess.run(command, shell=True)

            command = f"fslmaths {full_path_out} -dilM {full_path_out}"
            subprocess.run(command, shell=True)

            command = f"fslmaths {full_path_out} -ero {full_path_out}"
            subprocess.run(command, shell=True)

            exit()