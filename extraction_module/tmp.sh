#!/bin/bash
module load all
module load FSL ANTS
module load graphviz/2.46.0

NEW_REF='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/tmp_srr_template_debiased.nii.gz'
OUTPUT_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes/flirt'
RESULTS_FILE="$OUTPUT_DIR/metrics_results.txt"

GRAPH_FILE="$OUTPUT_DIR/metrics_graph.dot"
GRAPH_IMAGE="$OUTPUT_DIR/metrics_graph.svg"


# Créer ou vider les fichiers de résultats
echo "" > "$RESULTS_FILE"
echo "digraph Metrics {" > "$GRAPH_FILE"
echo "  rankdir=LR;" >> "$GRAPH_FILE"
echo "  node [shape=box, style=filled, fillcolor=lightgrey];" >> "$GRAPH_FILE"

# Boucle sur tous les fichiers _affine.nii.gz dans OUTPUT_DIR
for AFFINE_FILE in "$OUTPUT_DIR"/*_affine.nii.gz; do
    fname=$(basename "$AFFINE_FILE" _affine.nii.gz)
    atlas_id=$(echo "$fname" | grep -oP 'G\d+')

    echo "Calculating metrics for: $atlas_id" | tee -a "$RESULTS_FILE"

    # Mattes Mutual Information
    mattes=$(MeasureImageSimilarity -d 3 -m Mattes["$NEW_REF", "$AFFINE_FILE", 1, 64])
    echo "Mattes for $atlas_id: $mattes" | tee -a "$RESULTS_FILE"

    # Mean Squares Error
    mse=$(MeasureImageSimilarity -d 3 -m MeanSquares["$NEW_REF", "$AFFINE_FILE", 1, 3])
    echo "MSE for $atlas_id: $mse" | tee -a "$RESULTS_FILE"

    # Correlation Coefficient
    cc=$(MeasureImageSimilarity -d 3 -m CC["$NEW_REF", "$AFFINE_FILE", 1, 3])
    echo "CC for $atlas_id: $cc" | tee -a "$RESULTS_FILE"

    echo "***************************************************" | tee -a "$RESULTS_FILE"

    # Ajouter un nœud au graphe Graphviz
    echo "  \"$atlas_id\" [label=\"${atlas_id}\\nMattes: ${mattes}\\nMSE: ${mse}\\nCC: ${cc}\"];" >> "$GRAPH_FILE"
done

# Finaliser et générer le graphe
echo "}" >> "$GRAPH_FILE"
dot -Tsvg "$GRAPH_FILE" -o "$GRAPH_IMAGE"

echo "Tous les résultats sont dans $RESULTS_FILE"
echo "Graphe comparatif généré : $GRAPH_IMAGE"
