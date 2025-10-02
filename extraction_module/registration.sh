#!/bin/bash
module load all
module load FSL ANTS

# Chemin de base pour les sessions de Borgne
BASE_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne'
ATLAS_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes'
OUTPUT_BASE_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes/flirt'

# Créer le dossier de sortie s'il n'existe pas
mkdir -p "$OUTPUT_BASE_DIR"

# Parcourir chaque session dans Borgne
for SESSION in "$BASE_DIR"/ses*; do
    if [ -d "$SESSION" ]; then
        SESSION_NAME=$(basename "$SESSION")
        echo "=== Processing session: $SESSION_NAME ==="

        # Chemins spécifiques à la session
        REFERENCE="$SESSION/recons_rhesus/recon_template_space/srr_template_debiased.nii.gz"
        REFERENCE_MASK="$SESSION/recons_rhesus/recon_template_space/srr_template_mask.nii.gz"
        NEW_REF="$SESSION/recons_rhesus/recon_template_space/tmp_srr_template_debiased.nii.gz"
        OUTPUT_DIR="$OUTPUT_BASE_DIR/$SESSION_NAME"

        # Créer le dossier de sortie pour la session
        mkdir -p "$OUTPUT_DIR"

        # Appliquer le masque sur la référence
        fslmaths "$REFERENCE" -mul "$REFERENCE_MASK" "$NEW_REF"

        # Appliquer FLIRT sur tous les atlas
        echo "=== Running FLIRT on all atlases in $ATLAS_DIR for session $SESSION_NAME ==="
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
    fi
done

echo "=== Finished FLIRT for all sessions ==="
