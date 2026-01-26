import sys
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


# Dossier où sont stockés les résultats nnUNet
BASE_DIR = cfg.NNUNET_RESULTS_PATH

BASE_DIR = "/scratch/lbaptiste/data/nnUNet_trained_models"

MODELS = {
    "Dataset013_OnlyYoungSess": "nnUNetTrainerBias_1000epochs__nnUNetPlans__3d_fullres",
    "Dataset020_tmp_longi": "nnUNetTrainerBias_1000epochs__nnUNetPlans__3d_fullres",
}

CLASSES = ["1", "2", "3", "4"]


# ==============================
# FONCTION LECTURE summary.json
# ==============================

def extract_name(dataset):
    parts = dataset.split("_")
    return parts[1] if len(parts) > 1 else dataset

def load_summary(path):
    f = os.path.join(path, "summary.json")
    if not os.path.isfile(f):
        print(f"[WARNING] summary.json missing: {f}")
        return None
    with open(f, "r") as fp:
        return json.load(fp)


# ==============================
# EXTRACTION DES DICE
# ==============================

dice_by_class_models = {}  # structure : model -> class -> list[fold dice]

for model_name, trainer_dir in MODELS.items():
    model_path = os.path.join(BASE_DIR, model_name, trainer_dir)

    # Structure pour stocker les Dice d'un modèle
    dice_by_class = {cls: [] for cls in CLASSES}

    # Lire les folds
    for fold_idx in range(5):
        fold_path = os.path.join(model_path, f"fold_{fold_idx}", "validation")
        summary = load_summary(fold_path)
        if summary is None:
            continue

        # Ton format : summary["mean"][cls]["Dice"]
        for cls in CLASSES:
            dice_value = summary["mean"][cls]["Dice"]
            dice_by_class[cls].append(dice_value)

    dice_by_class_models[model_name] = dice_by_class


# ==============================
# 1) BOXPLOTS
# ==============================

models = list(MODELS.keys())
models_name = [extract_name(m) for m in models]

fig, axes = plt.subplots(1, len(CLASSES), figsize=(20, 5), sharey=True)

for idx, cls in enumerate(CLASSES):
    data = [dice_by_class_models[m][cls] for m in models]
    axes[idx].boxplot(data, labels=models_name)
    axes[idx].set_title(f"Classe {cls}")
    axes[idx].set_ylabel("Dice")

plt.tight_layout()
plt.savefig("tmp.png")


# ==============================
# 2) CLASSEMENT GLOBAL
# ==============================

ranking = []

for model in models:
    all_values = []
    for cls in CLASSES:
        all_values.extend(dice_by_class_models[model][cls])
    mean_dice = float(np.mean(all_values))
    ranking.append((model, mean_dice))

ranking_df = pd.DataFrame(ranking, columns=["Model", "Mean Dice"])
ranking_df = ranking_df.sort_values("Mean Dice", ascending=False)

print("\n====================")
print("CLASSEMENT GLOBAL")
print("====================")
print(ranking_df.to_string(index=False))


# ==============================
# 3) CLASSEMENT PAR CLASSE
# ==============================

rows = []
for cls in CLASSES:
    for model in models:
        mean_cls = np.mean(dice_by_class_models[model][cls])
        rows.append([cls, model, mean_cls])

ranking_per_class = pd.DataFrame(rows, columns=["Class", "Model", "Dice Mean"])
ranking_per_class = ranking_per_class.sort_values(["Class", "Dice Mean"],
                                                  ascending=[True, False])

print("\n====================")
print("CLASSEMENT PAR CLASSE")
print("====================")
print(ranking_per_class.to_string(index=False))