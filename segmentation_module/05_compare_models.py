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
    match = re.search(r'\d+', filename)
    return match.group() if match else filename


def load_nifti_labels(path):
    img = nib.load(path)
    return np.asanyarray(img.dataobj).astype(np.int16)


def dice_per_label(mask, reference, label):
    m = (mask == label)
    r = (reference == label)
    intersection = np.sum(m & r)
    total = np.sum(m) + np.sum(r)
    return (2. * intersection) / total if total > 0 else 1.0

database = {}
for model_name, path in folders.items():
    for f in os.listdir(path):
        if f.endswith('.nii.gz'):
            subject_id = extract_id(f)
            if subject_id not in database:
                database[subject_id] = {}
            database[subject_id][model_name] = os.path.join(path, f)

common_ids = [sid for sid, paths in database.items() if len(paths) == len(folders)]
print(f"Sujets trouvés dans tous les dossiers : {len(common_ids)} / {len(database)}")

results_list = []

for sid in tqdm(common_ids, desc="Comparaison multi-noms"):
    try:
        # Chargement des masques pour ce sujet
        masks_dict = {name: load_nifti_labels(path) for name, path in database[sid].items()}

        # Vérification des dimensions (crucial si noms différents)
        shapes = [m.shape for m in masks_dict.values()]
        if len(set(shapes)) > 1:
            print(f"⚠️ Dimensions incohérentes pour ID {sid}: {shapes}. Sujet sauté.")
            continue

        # Consensus (Majority Voting)
        masks_stack = np.array(list(masks_dict.values()))
        consensus = stats.mode(masks_stack, axis=0, keepdims=False)[0]

        # Métriques
        for name in folders.keys():
            for l in labels_interest:
                score = dice_per_label(masks_dict[name], consensus, l)
                results_list.append({
                    "ID": sid,
                    "Modèle": name,
                    "Label": f"Label {l}",
                    "Dice": score
                })
    except Exception as e:
        print(f"Erreur sur ID {sid}: {e}")

# 3. ANALYSE
df = pd.DataFrame(results_list)
pivot_summary = df.groupby(['Modèle', 'Label'])['Dice'].mean().unstack()

print("\n--- Dice Moyen vs Consensus ---")
print(pivot_summary.round(4))

# Visualisation rapide
sns.catplot(data=df, x="Label", y="Dice", hue="Modèle", kind="box", height=6, aspect=1.5)
plt.title("Distribution des scores par rapport au Consensus")
plt.show()