import os
import nibabel as nib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm


def load_nifti_mask(path):
    """Charge un volume NIfTI et le binarise."""
    img = nib.load(path)
    data = img.get_fdata()
    return (data > 0.5).astype(np.uint8)


def dice_coeff(mask1, mask2):
    """Calcul du Dice pour des volumes 3D."""
    intersection = np.sum(mask1 & mask2)
    total = np.sum(mask1) + np.sum(mask2)
    if total == 0: return 1.0
    return (2. * intersection) / total


# 1. Configuration
folders = {
    "LongiSeg": "tmp_borgne_data/results_segmentations",
    "LongiSegDiff": "tmp_borgne_data/results_segmentations_diff",
    "nnUNetLongi": "tmp_borgne_data/results_segmentations_nnunet_longi"
}

# On récupère la liste des fichiers (on suppose qu'ils ont les mêmes noms partout)
filenames = [f for f in os.listdir(list(folders.values())[0]) if f.endswith('.nii.gz')]
model_names = list(folders.keys())

pairwise_dice = np.zeros((len(model_names), len(model_names)))
consensus_scores = {name: [] for name in model_names}

# 2. Boucle de calcul
for fname in tqdm(filenames, desc="Analyse des volumes 3D"):
    try:
        masks = []
        for name in model_names:
            masks.append(load_nifti_mask(os.path.join(folders[name], fname)))

        masks_stack = np.array(masks)

        # A. Consensus (Majority Voting)
        # On calcule la moyenne sur l'axe des modèles : si > 0.5, la majorité l'emporte
        consensus = (np.mean(masks_stack, axis=0) > 0.5).astype(np.uint8)

        # B. Comparaisons
        for i in range(len(model_names)):
            # Score vs Consensus
            c_score = dice_coeff(masks_stack[i], consensus)
            consensus_scores[model_names[i]].append(c_score)

            # Pairwise (entre modèles)
            for j in range(i, len(model_names)):
                p_score = dice_coeff(masks_stack[i], masks_stack[j])
                pairwise_dice[i, j] += p_score
                if i != j: pairwise_dice[j, i] += p_score

    except Exception as e:
        print(f"Erreur sur le fichier {fname}: {e}")

# 3. Résultats et Visualisation
pairwise_dice /= len(filenames)

# Heatmap de similarité
plt.figure(figsize=(8, 6))
sns.heatmap(pd.DataFrame(pairwise_dice, index=model_names, columns=model_names),
            annot=True, cmap="YlGnBu", vmin=0, vmax=1)
plt.title("Matrice de similarité (Dice Moyen)")
plt.savefig("pairwise_dice_heatmap.png")
plt.close()

# Ranking
print("\n--- Classement par rapport au Consensus (Simulated GT) ---")
ranking = []
for name in model_names:
    avg_dice = np.mean(consensus_scores[name])
    std_dice = np.std(consensus_scores[name])
    ranking.append({"Modèle": name, "Dice Consensus": avg_dice, "Std": std_dice})

print(pd.DataFrame(ranking).sort_values(by="Dice Consensus", ascending=False).to_string(index=False))