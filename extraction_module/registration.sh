#!/bin/bash
module load all
module load FSL ANTS  

REFERENCE='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses03/recons_rhesus/recon_template_space/srr_template_debiased.nii.gz'
REFERENCE_MASK='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses03/recons_rhesus/recon_template_space/srr_template_mask.nii.gz'
NEW_REF='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses03/recons_rhesus/recon_template_space/tmp_srr_template_debiased.nii.gz'

ATLAS_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes'
OUTPUT_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes/flirt'
mkdir -p "$OUTPUT_DIR"

# Appliquer le masque sur la référence
fslmaths "$REFERENCE" -mul "$REFERENCE_MASK" "$NEW_REF"

echo "=== Running FLIRT on all atlases in $ATLAS_DIR ==="

for MOVING in "$ATLAS_DIR"/*.nii.gz; do
    fname=$(basename "$MOVING" .nii.gz)
    echo "Processing atlas: $fname"

    flirt \
        -in "$MOVING" \
        -ref "$NEW_REF" \
        -out "$OUTPUT_DIR/${fname}_affine.nii.gz" \
        -omat "$OUTPUT_DIR/${fname}_affine.mat" \
        -dof 12 \
        -cost mutualinfo \
        -searchrx -180 180 \
        -searchry -180 180 \
        -searchrz -180 180 \
        -interp spline
done

echo "=== Finished FLIRT for all atlases ==="
