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
    atlas_path = cfg.ATLAS_GHOLIPOUR_PATH_NIOLON

    for ts in range(21, 38):
        filename_in = f"STA{ts}_all_reg_LR.nii.gz"
        filename_path_in = os.path.join(atlas_path, filename_in)

        filename_out = f"STA{ts}_all_reg_LR_dilall.nii.gz"
        filename_path_out = os.path.join(atlas_path, filename_out)

        print("Computing ", filename_in)

        command = f"fslmaths {filename_path_in} -dilM -dilM -dilM -dilM -dilall {filename_path_out}"
        subprocess.run(command, shell=True)

        command = f"fslmaths {filename_path_out} -uthr 1 {filename_path_out}"
        subprocess.run(command, shell=True)

        command = f"fslmaths {filename_path_out} -dilM {filename_path_out}"
        subprocess.run(command, shell=True)

        command = f"fslmaths {filename_path_out} -ero {filename_path_out}"
        subprocess.run(command, shell=True)

        exit()