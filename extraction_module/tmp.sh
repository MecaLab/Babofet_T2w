#!/bin/bash
module load all
module load FSL ANTS

REFERENCE_MASK='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/srr_template_mask.nii.gz'
NEW_REF='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/tmp_srr_template_debiased.nii.gz'
OUTPUT_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes/flirt'
RESULTS_FILE="$OUTPUT_DIR/metrics_results.csv"
PLOT_DIR="$OUTPUT_DIR/plots"
mkdir -p "$PLOT_DIR"


# En-tête pour le fichier CSV
echo "Atlas,Mattes,MSE,CC" > "$RESULTS_FILE"

# Boucle sur tous les fichiers _affine.nii.gz dans OUTPUT_DIR
for AFFINE_FILE in "$OUTPUT_DIR"/*_affine.nii.gz; do
    fname=$(basename "$AFFINE_FILE" _affine.nii.gz)
    atlas_id=$(echo "$fname" | grep -oP 'G\d+')

    # Mattes Mutual Information
    mattes=$(MeasureImageSimilarity -d 3 -m Mattes["$NEW_REF", "$AFFINE_FILE", 1, 64] -x "$REFERENCE_MASK")
    # Mean Squares Error
    mse=$(MeasureImageSimilarity -d 3 -m MeanSquares["$NEW_REF", "$AFFINE_FILE", 1, 3] -x "$REFERENCE_MASK")
    # Correlation Coefficient
    cc=$(MeasureImageSimilarity -d 3 -m CC["$NEW_REF", "$AFFINE_FILE", 1, 3] -x "$REFERENCE_MASK")

    echo "$atlas_id,$mattes,$mse,$cc" >> "$RESULTS_FILE"
done


echo "Les courbes sont disponibles dans $PLOT_DIR/"
