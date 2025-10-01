#!/bin/bash
module load all
module load FSL ANTS

REFERENCE='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/srr_template_debiased.nii.gz'
REFERENCE_MASK='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/srr_template_mask.nii.gz'
NEW_REF='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/tmp_srr_template_debiased.nii.gz'
OUTPUT_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes/flirt'
RESULTS_FILE="$OUTPUT_DIR/metrics_results.csv"
PLOT_DIR="$OUTPUT_DIR/plots"
mkdir -p "$PLOT_DIR"

# Appliquer le masque sur la référence
fslmaths "$REFERENCE" -mul "$REFERENCE_MASK" "$NEW_REF"

# En-tête pour le fichier CSV
echo "Atlas,Mattes,MSE,CC" > "$RESULTS_FILE"

# Boucle sur tous les fichiers _affine.nii.gz dans OUTPUT_DIR
for AFFINE_FILE in "$OUTPUT_DIR"/*_affine.nii.gz; do
    fname=$(basename "$AFFINE_FILE" _affine.nii.gz)
    atlas_id=$(echo "$fname" | grep -oP 'G\d+')

    # Mattes Mutual Information
    mattes=$(MeasureImageSimilarity -d 3 -m Mattes["$NEW_REF", "$AFFINE_FILE", 1, 64])
    # Mean Squares Error
    mse=$(MeasureImageSimilarity -d 3 -m MeanSquares["$NEW_REF", "$AFFINE_FILE", 1, 3])
    # Correlation Coefficient
    cc=$(MeasureImageSimilarity -d 3 -m CC["$NEW_REF", "$AFFINE_FILE", 1, 3])

    echo "$atlas_id,$mattes,$mse,$cc" >> "$RESULTS_FILE"
done

# Générer les courbes avec Python/matplotlib
cat << 'EOF' | python3 -
import pandas as pd
import matplotlib.pyplot as plt
import os

# Lire les données
data = pd.read_csv("$RESULTS_FILE")

# Extraire les atlas (ex: G85, G122)
atlases = data["Atlas"]
mattes = data["Mattes"]
mse = data["MSE"]
cc = data["CC"]

# Créer les courbes
os.makedirs("$PLOT_DIR", exist_ok=True)

# Courbe Mattes
plt.figure()
plt.plot(atlases, mattes, marker='o', label="Mattes")
plt.title("Mattes Mutual Information par Atlas")
plt.xlabel("Atlas")
plt.ylabel("Valeur de Mattes")
plt.grid(True)
plt.savefig("$PLOT_DIR/mattes_plot.svg", format="svg")
plt.close()

# Courbe MSE
plt.figure()
plt.plot(atlases, mse, marker='o', color='orange', label="MSE")
plt.title("Mean Squares Error par Atlas")
plt.xlabel("Atlas")
plt.ylabel("Valeur de MSE")
plt.grid(True)
plt.savefig("$PLOT_DIR/mse_plot.svg", format="svg")
plt.close()

# Courbe CC
plt.figure()
plt.plot(atlases, cc, marker='o', color='green', label="CC")
plt.title("Correlation Coefficient par Atlas")
plt.xlabel("Atlas")
plt.ylabel("Valeur de CC")
plt.grid(True)
plt.savefig("$PLOT_DIR/cc_plot.svg", format="svg")
plt.close()
EOF

echo "Les courbes sont disponibles dans $PLOT_DIR/"
