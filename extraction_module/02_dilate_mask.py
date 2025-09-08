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
    filename_out = os.path.join(seg_folder, f"ONPRC_G110_NFseg_3_dilall_dilM.nii.gz")

    print(f"Computing: {filename_in}")

    """command = f"fslmaths {filename_in} -dilM -dilM -dilM -dilM -dilall {filename_out}"
    subprocess.run(command, shell=True)

    command = f"fslmaths {filename_out} -uthr 1 {filename_out}"
    subprocess.run(command, shell=True, check=True)

    command = f"fslmaths {filename_out} -dilM {filename_out}"
    subprocess.run(command, shell=True, check=True)

    command = f"fslmaths {filename_out} -ero {filename_out}"
    subprocess.run(command, shell=True)"""

    n_dilations = 4

    tmp_dir = os.path.join(seg_folder, "tmp_dilation")

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    subprocess.run(f"mkdir -p {tmp_dir}", shell=True)

    # Extraire chaque label
    subprocess.run(f"fslmaths {filename_in} -uth 0.5 -ut 1.5 -bin {tmp_dir}/label_1.nii.gz", shell=True,
                   check=True)  # Hémisphère gauche
    subprocess.run(f"fslmaths {filename_in} -uth 1.5 -ut 2.5 -bin {tmp_dir}/label_2.nii.gz", shell=True,
                   check=True)  # Hémisphère droit
    subprocess.run(f"fslmaths {filename_in} -uth 2.5 -ut 3.5 -bin {tmp_dir}/label_3.nii.gz", shell=True,
                   check=True)  # Cervelet

    # Créer un masque des zones vides (valeur 0)
    subprocess.run(f"fslmaths {filename_in} -binv {tmp_dir}/empty.nii.gz", shell=True, check=True)

    # Dilater chaque label dans les zones vides
    for label in [1, 2, 3]:
        cmd = f"fslmaths {tmp_dir}/label_{label}.nii.gz "
        cmd += "-dilM " * n_dilations  # Appliquer n dilatations
        cmd += f"-mas {tmp_dir}/empty.nii.gz {tmp_dir}/label_{label}_dilated.nii.gz"
        subprocess.run(cmd, shell=True, check=True)

    # Fusionner les dilatations avec le masque original
    cmd = f"fslmaths {filename_in} "
    cmd += f"-add {tmp_dir}/label_1_dilated.nii.gz "
    cmd += f"-add {tmp_dir}/label_2_dilated.nii.gz "
    cmd += f"-add {tmp_dir}/label_3_dilated.nii.gz "
    cmd += f"{filename_out}"
    subprocess.run(cmd, shell=True, check=True)

    # Nettoyer les fichiers temporaires
    subprocess.run(f"rm -rf {tmp_dir}", shell=True)