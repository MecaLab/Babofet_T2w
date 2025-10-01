module load all
module load FSL ANTS

REFERENCE='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/srr_template_debiased.nii.gz'
REFERENCE_MASK='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/srr_template_mask.nii.gz'
NEW_REF='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/tmp_srr_template_debiased.nii.gz'

MOVING='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes/ONPRC_G122_Norm.nii.gz'
MOVING_MASK='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Segmentations/structures_dilated/ONPRC_G122_NFseg_bm.nii.gz'
SMOOTHED_PARCELLATIONS='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Segmentations/ONPRC_G122_NFseg.nii.gz'

OUTPUT_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes/flirt'
mkdir -p "$OUTPUT_DIR"

fslmaths "$REFERENCE" -mul "$REFERENCE_MASK" "$NEW_REF"

echo "Measure image similarity Mattes for registration 122"
MeasureImageSimilarity \
  -d 3 \
  -m Mattes["$NEW_REF", "$OUTPUT_DIR/affine_122.nii.gz", 1, 64]

echo "Measure image similarity Mattes for registration 85"
MeasureImageSimilarity \
  -d 3 \
  -m Mattes["$NEW_REF", "$OUTPUT_DIR/affine_85.nii.gz", 1, 64]

echo "***************************************************"

echo "Measure image similarity MSE for registration 122"
MeasureImageSimilarity \
  -d 3 \
  -m MeanSquares["$NEW_REF", "$OUTPUT_DIR/affine_122.nii.gz", 1, 3]

echo "Measure image similarity MSE for registration 85"
MeasureImageSimilarity \
  -d 3 \
  -m MeanSquares["$NEW_REF", "$OUTPUT_DIR/affine_85.nii.gz", 1, 3]


echo "***************************************************"

echo "Measure image similarity CC for registration 122"
MeasureImageSimilarity \
  -d 3 \
  -m CC["$NEW_REF", "$OUTPUT_DIR/affine_122.nii.gz", 1, 3]

echo "Measure image similarity CC for registration 85"
MeasureImageSimilarity \
  -d 3 \
  -m CC["$NEW_REF", "$OUTPUT_DIR/affine_85.nii.gz", 1, 3]