import sys
import os
import json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


# Dossier où sont stockés les résultats nnUNet
BASE_DIR = cfg.NNUNET_RESULTS_PATH

MODELS = [
    "Dataset010_Starter",
    "Dataset011_DebiasData",
    "Dataset012_FullExp"
]

CONFIG = "3d_fullres"   # ou ton config spécifique
TRAINER = None          # si tu veux forcer un trainer spécifique (sinon auto-detect)


def load_summary_json(path):
    if not os.path.isfile(path):
        print(f"[WARN] summary.json not found: {path}")
        return None
    with open(path, "r") as f:
        return json.load(f)


def find_trainer_dir(dataset_dir):
    """Détecte automatiquement le dossier du trainer."""
    for d in os.listdir(dataset_dir):
        if os.path.isdir(os.path.join(dataset_dir, d)) and "__nnUNetPlans" in d:
            return d
    return None


all_results = {}

for model in MODELS:
    dataset_dir = os.path.join(BASE_DIR, model)

    trainer_dir = find_trainer_dir(dataset_dir)
    if trainer_dir is None:
        print(f"[ERROR] Aucun trainer trouvé dans {dataset_dir}")
        continue

    summary_path = os.path.join(dataset_dir, trainer_dir, "summary.json")
    summary = load_summary_json(summary_path)

    if summary is None:
        continue

    # structure nnUNet v2
    dice_per_class = summary["results"]["mean"]["Dice"]
    hd95_per_class = summary["results"]["mean"].get("HD95", None)

    # Convert to numpy for safety
    dice_means = {cls: np.mean(vals) for cls, vals in dice_per_class.items()}
    dice_stds = {cls: np.std(vals) for cls, vals in dice_per_class.items()}

    if hd95_per_class:
        hd95_means = {cls: np.mean(vals) for cls, vals in hd95_per_class.items()}
        hd95_stds = {cls: np.std(vals) for cls, vals in hd95_per_class.items()}
    else:
        hd95_means = hd95_stds = {}

    all_results[model] = {
        "dice_mean": dice_means,
        "dice_std": dice_stds,
        "hd95_mean": hd95_means,
        "hd95_std": hd95_stds
    }


# ---------- CONSTRUCTION DU TABLEAU FINAL ----------
rows = []

for model, metrics in all_results.items():
    classes = metrics["dice_mean"].keys()
    for cls in classes:
        rows.append({
            "Model": model,
            "Class": cls,
            "Dice Mean": metrics["dice_mean"][cls],
            "Dice Std": metrics["dice_std"][cls],
            "HD95 Mean": metrics["hd95_mean"].get(cls, None),
            "HD95 Std": metrics["hd95_std"].get(cls, None)
        })

df = pd.DataFrame(rows)
df = df.sort_values(by=["Class", "Model"])

print("\n========= COMPARAISON DES MODELS nnUNet =========\n")
print(df.to_string(index=False))
