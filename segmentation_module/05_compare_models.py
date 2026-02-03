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

def load_nifti(path):
    img = nib.load(path)
    return np.asanyarray(img.dataobj).astype(np.int16)

def dice_coeff(mask, ref, label):
    m = (mask == label)
    r = (ref == label)
    intersection = np.sum(m & r)
    total = np.sum(m) + np.sum(r)
    return (2. * intersection) / total if total > 0 else 1.0

def compute_all_metrics(mask, ref, label):
    m = (mask == label)
    r = (ref == label)

    tp = np.sum(m & r)
    fp = np.sum(m & ~r)
    fn = np.sum(~m & r)

    # Dice
    dice = (2. * tp) / (2. * tp + fp + fn) if (2. * tp + fp + fn) > 0 else 1.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    vol_mask = np.sum(m)
    vol_ref = np.sum(r)
    v_err = (vol_mask - vol_ref) / vol_ref if vol_ref > 0 else 0.0

    return dice, precision, recall, v_err

database = {}
for model_name, path in folders.items():
    for f in os.listdir(path):
        if f.endswith('.nii.gz'):
            sid = extract_id(f)
            if sid not in database: database[sid] = {}
            database[sid][model_name] = os.path.join(path, f)

common_ids = [sid for sid, p in database.items() if len(p) == len(folders)]
print(f"Sujets à traiter : {len(common_ids)}")


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

    for name, mask in [("Model_A", m1), ("Model_B", m2), ("Model_C", m3)]:
        for l in labels_interest:
            d, p, r, v = compute_all_metrics(mask, consensus, l)
            results.append({
                "Sujet": sid, "Modèle": name, "Label": f"L{l}",
                "Dice": d, "Précision": p, "Recall": r, "Vol_Error": v
            })

# 3. SYNTHÈSE
df = pd.DataFrame(results)
summary = df.groupby(['Modèle', 'Label'])[['Dice', 'Précision', 'Recall', 'Vol_Error']].mean()

print("\n--- ANALYSE DÉTAILLÉE PAR RAPPORT AU CONSENSUS ---")
print(summary.round(4))