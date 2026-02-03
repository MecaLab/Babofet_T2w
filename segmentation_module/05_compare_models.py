import os
import re
import nibabel as nib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy import stats

# --- CONFIGURATION ---
folders = {
    "LongiSeg": "tmp_borgne_data/results_segmentations",
    "LongiSegDiff": "tmp_borgne_data/results_segmentations_diff",
    "nnUNetLongi": "tmp_borgne_data/results_segmentations_nnunet_longi"
}
labels_interest = [1, 2, 3, 4]

def extract_id(filename):
    """Extrait l'ID (ex: '001') du nom du fichier."""
    match = re.search(r'\d+', filename)
    return match.group() if match else filename

def load_nifti(path):
    """Charge le NIfTI en mémoire."""
    img = nib.load(path)
    return np.asanyarray(img.dataobj).astype(np.int16)

def dice_coeff(mask, ref, label):
    """Calcule le coefficient de Dice pour un label donné."""
    m = (mask == label)
    r = (ref == label)
    intersection = np.sum(m & r)
    total = np.sum(m) + np.sum(r)
    return (2. * intersection) / total if total > 0 else 1.0

# 1. RÉPERTORIER LES FICHIERS
database = {}
for model_name, path in folders.items():
    for f in os.listdir(path):
        if f.endswith('.nii.gz'):
            sid = extract_id(f)
            if sid not in database: database[sid] = {}
            database[sid][model_name] = os.path.join(path, f)

# On garde les IDs complets (présents dans les 3 dossiers)
common_ids = [sid for sid, p in database.items() if len(p) == len(folders)]
print(f"Sujets à traiter : {len(common_ids)}")

# 2. TRAITEMENT SÉQUENTIEL
results = []

for sid in tqdm(common_ids, desc="Analyse en cours"):
    m1 = load_nifti(database[sid]["LongiSeg"])
    m2 = load_nifti(database[sid]["LongiSegDiff"])
    m3 = load_nifti(database[sid]["nnUNetLongi"])

    # --- CONSENSUS RAPIDE (NUMPY) ---
    # Logique du vote majoritaire pour 3 modèles :
    # Si m1 == m2, on prend m1. Sinon, si m1 == m3, on prend m1.
    # Sinon, on prend m2 (car si m2 == m3, c'est m2 qui gagne).
    consensus = np.where((m1 == m2) | (m1 == m3), m1, m2)

    # Calcul des scores
    for name, mask in [("LongiSeg", m1), ("LongiSegDiff", m2), ("nnUNetLongi", m3)]:
        for l in labels_interest:
            score = dice_coeff(mask, consensus, l)
            results.append({
                "Sujet": sid,
                "Modèle": name,
                "Label": f"L{l}",
                "Dice": score
            })

df = pd.DataFrame(results)
summary = df.groupby(['Modèle', 'Label'])['Dice'].mean().unstack()

print("\n--- DICE MOYEN (VS CONSENSUS) ---")
print(summary.round(4))


summary.plot(kind='bar', figsize=(10, 6))
plt.title("Performance par Label et par Modèle")
plt.ylabel("Dice Score")
plt.ylim(0, 1)
plt.legend(title="Labels", bbox_to_anchor=(1.05, 1))
plt.tight_layout()
plt.savefig("model_comparison_dice_scores.png")