#!/bin/bash
module load all
module load FSL ANTS

# Chemin de base pour les sessions de Borgne
BASE_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne'
OUTPUT_BASE_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes/flirt'

# Parcourir chaque session dans Borgne
for SESSION in "$BASE_DIR"/ses*; do
    if [ -d "$SESSION" ]; then
        SESSION_NAME=$(basename "$SESSION")
        echo "=== Calculating metrics for session: $SESSION_NAME ==="

        # Chemins spécifiques à la session
        REFERENCE_MASK="$SESSION/recons_rhesus/recon_template_space/srr_template_mask.nii.gz"
        NEW_REF="$SESSION/recons_rhesus/recon_template_space/tmp_srr_template_debiased.nii.gz"
        OUTPUT_DIR="$OUTPUT_BASE_DIR/$SESSION_NAME"
        RESULTS_FILE="$OUTPUT_DIR/metrics_results.csv"

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
    fi
done

echo "=== Finished calculating metrics for all sessions ==="
