module load all
module load FSL ANTS  

REFERENCE='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/srr_template_debiased.nii.gz'
REFERENCE_MASK='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/srr_template_mask.nii.gz'
NEW_REF='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/tmp_srr_template_debiased.nii.gz'

MOVING='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes/ONPRC_G85_Norm.nii.gz'
MOVING_MASK='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Segmentations/structures_dilated/ONPRC_G85_NFseg_bm.nii.gz'
SMOOTHED_PARCELLATIONS='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Segmentations/ONPRC_G85_NFseg.nii.gz'


OUTPUT_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes/flirt'
mkdir -p "$OUTPUT_DIR"

fslmaths "$REFERENCE" -mul "$REFERENCE_MASK" "$NEW_REF"

# affine first
echo "Running FLIRT..."
flirt \
	-in "$MOVING" \
	-ref "$NEW_REF" \
	-out "$OUTPUT_DIR/affine.nii.gz" \
	-omat "$OUTPUT_DIR/affine.mat" \
	-dof 12 \
	-cost mutualinfo \
	-searchrx -180 180 \
	-searchry -180 180 \
	-searchrz -180 180 \
	-interp spline