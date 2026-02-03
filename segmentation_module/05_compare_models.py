import os
import nibabel as nib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy import stats


def load_nifti_labels(path):
    img = nib.load(path)
    return np.asanyarray(img.dataobj).astype(np.int16)


def dice_per_label(mask, reference, label):
    """Calcul du Dice pour un label spécifique."""
    m = (mask == label)
    r = (reference == label)
    intersection = np.sum(m & r)
    total = np.sum(m) + np.sum(r)
    if total == 0: return 1.0
    return (2. * intersection) / total


# 1. Configuration
folders = {
    "LongiSeg": "tmp_borgne_data/results_segmentations",
    "LongiSegDiff": "tmp_borgne_data/results_segmentations_diff",
    "nnUNetLongi": "tmp_borgne_data/results_segmentations_nnunet_longi"
}

# On définit nos labels (0=bg, 1, 2, 3, 4)
labels_interest = [1, 2, 3, 4]
filenames = [f for f in os.listdir(list(folders.values())[0]) if f.endswith('.nii.gz')]
model_names = list(folders.keys())

# Data structure pour stocker les scores
results_list = []

# 2. Boucle de traitement
for fname in tqdm(filenames, desc="Analyse Multi-classe (5 labels)"):
    try:
        # Chargement de tous les modèles pour cette image
        masks_dict = {name: load_nifti_labels(os.path.join(folders[name], fname)) for name in model_names}

        # Création d'un stack pour le consensus
        masks_stack = np.array(list(masks_dict.values()))  # Shape: (N_models, H, W, D)

        # Consensus par vote majoritaire
        # stats.mode renvoie (valeurs, comptes). On prend [0] pour les valeurs.
        consensus = stats.mode(masks_stack, axis=0, keepdims=False)[0]

        # Comparaison de chaque modèle au consensus pour chaque label
        for name in model_names:
            for l in labels_interest:
                score = dice_per_label(masks_dict[name], consensus, l)
                results_list.append({
                    "Image": fname,
                    "Modèle": name,
                    "Label": f"Label {l}",
                    "Dice": score
                })

    except Exception as e:
        print(f"\nErreur sur {fname}: {e}")

# 3. Analyse et Visualisation
df = pd.DataFrame(results_list)

# Affichage des moyennes par Label et par Modèle
summary = df.groupby(['Modèle', 'Label'])['Dice'].agg(['mean', 'std']).reset_index()
pivot_summary = summary.pivot(index='Modèle', columns='Label', values='mean')

print("\n--- Score Dice Moyen par rapport au Consensus ---")
print(pivot_summary.round(4))

# Visualisation Boxplot pour voir la dispersion (stabilité)
plt.figure(figsize=(12, 7))
sns.boxplot(data=df, x="Label", y="Dice", hue="Modèle")
plt.title("Dispersion du Dice par Label (vs Consensus)")
plt.ylim(0, 1.02)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig("dice_comparison_boxplot.png", dpi=300)
plt.close()