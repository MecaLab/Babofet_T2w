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