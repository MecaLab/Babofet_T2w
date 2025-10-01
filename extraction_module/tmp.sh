#!/bin/bash
module load all
module load FSL ANTS

NEW_REF='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/tmp_srr_template_debiased.nii.gz'

OUTPUT_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes/flirt'
RESULTS_FILE="$OUTPUT_DIR/metrics_results.txt"


# Créer ou vider le fichier de résultats
echo "" > "$RESULTS_FILE"

# Boucle sur tous les fichiers _affine.nii.gz dans OUTPUT_DIR
for AFFINE_FILE in "$OUTPUT_DIR"/*_affine.nii.gz; do
    fname=$(basename "$AFFINE_FILE" _affine.nii.gz)
    echo "Calculating metrics for: $fname" | tee -a "$RESULTS_FILE"

    # Extraire l'âge ou l'identifiant de l'atlas (ex. G85, G122)
    atlas_id=$(echo "$fname" | grep -oP 'G\d+')

    # Mattes Mutual Information
    echo "Mattes for $atlas_id:" | tee -a "$RESULTS_FILE"
    MeasureImageSimilarity -d 3 -m Mattes["$NEW_REF", "$AFFINE_FILE", 1, 64] | tee -a "$RESULTS_FILE"

    # Mean Squares Error
    echo "MSE for $atlas_id:" | tee -a "$RESULTS_FILE"
    MeasureImageSimilarity -d 3 -m MeanSquares["$NEW_REF", "$AFFINE_FILE", 1, 3] | tee -a "$RESULTS_FILE"

    # Correlation Coefficient
    echo "CC for $atlas_id:" | tee -a "$RESULTS_FILE"
    MeasureImageSimilarity -d 3 -m CC["$NEW_REF", "$AFFINE_FILE", 1, 3] | tee -a "$RESULTS_FILE"

    echo "***************************************************" | tee -a "$RESULTS_FILE"
done

echo "All metrics saved to $RESULTS_FILE"
