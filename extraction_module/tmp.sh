#!/bin/bash
module load all
module load FSL ANTS
module load graphviz/2.46.0

REFERENCE='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/srr_template_debiased.nii.gz'
REFERENCE_MASK='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/srr_template_mask.nii.gz'
NEW_REF='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/tmp_srr_template_debiased.nii.gz'
OUTPUT_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes/flirt'
RESULTS_FILE="$OUTPUT_DIR/metrics_results.txt"
PLOT_DIR="$OUTPUT_DIR/plots"
mkdir -p "$PLOT_DIR"

# Appliquer le masque sur la référence
fslmaths "$REFERENCE" -mul "$REFERENCE_MASK" "$NEW_REF"

# Créer ou vider le fichier de résultats
echo "" > "$RESULTS_FILE"

# En-tête pour le fichier CSV
echo "Atlas,Mattes,MSE,CC" > "$OUTPUT_DIR/metrics_summary.csv"

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

    # Écrire dans le fichier CSV pour gnuplot
    echo "$atlas_id,$mattes,$mse,$cc" >> "$OUTPUT_DIR/metrics_summary.csv"
done

# Générer les graphiques avec gnuplot
cat <<EOF | gnuplot
set terminal pngcairo enhanced fontsize 10
set output "$PLOT_DIR/mattes_plot.png"
set title "Mattes Mutual Information par Atlas"
set xlabel "Atlas"
set ylabel "Valeur de Mattes"
set style data histograms
set style fill solid
set boxwidth 0.7
plot "$OUTPUT_DIR/metrics_summary.csv" using 2:xtic(1) title "Mattes", '' using 0:0:0 with boxes lc rgb "grey" notitle
EOF

cat <<EOF | gnuplot
set terminal pngcairo enhanced fontsize 10
set output "$PLOT_DIR/mse_plot.png"
set title "Mean Squares Error par Atlas"
set xlabel "Atlas"
set ylabel "Valeur de MSE"
set style data histograms
set style fill solid
set boxwidth 0.7
plot "$OUTPUT_DIR/metrics_summary.csv" using 3:xtic(1) title "MSE", '' using 0:0:0 with boxes lc rgb "grey" notitle
EOF

cat <<EOF | gnuplot
set terminal pngcairo enhanced fontsize 10
set output "$PLOT_DIR/cc_plot.png"
set title "Correlation Coefficient par Atlas"
set xlabel "Atlas"
set ylabel "Valeur de CC"
set style data histograms
set style fill solid
set boxwidth 0.7
plot "$OUTPUT_DIR/metrics_summary.csv" using 4:xtic(1) title "CC", '' using 0:0:0 with boxes lc rgb "grey" notitle
EOF

echo "Tous les résultats et graphiques sont dans $OUTPUT_DIR et $PLOT_DIR"
