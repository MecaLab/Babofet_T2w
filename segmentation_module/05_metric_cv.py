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

MODELS = {
    "Dataset010_Starter": "nnUNetTrainer_2000epochs__nnUNetPlans__3d_fullres",
    "Dataset011_DebiasData": "nnUNetTrainer_2000epochs__nnUNetPlans__3d_fullres",
    "Dataset012_FullExp": "nnUNetTrainerBias_2000epochs__nnUNetPlans__3d_fullres"
}

def load_summary(path):
    """Lit le summary.json d'un fold."""
    f = os.path.join(path, "summary.json")
    if not os.path.isfile(f):
        print(f"[WARNING] summary.json missing: {f}")
        return None
    with open(f, "r") as fp:
        return json.load(fp)


all_results = {}

for model_name, trainer_dir in MODELS.items():

    model_path = os.path.join(BASE_DIR, model_name, trainer_dir)

    dice_by_class = {cls: [] for cls in ["1", "2", "3", "4"]}

    for fold in range(5):
        fold_path = os.path.join(model_path, f"fold_{fold}", "validation")
        summary = load_summary(fold_path)
        if summary is None:
            continue

        # Ton format : summary["mean"][cls]["Dice"]
        for cls in dice_by_class:
            dice_value = summary["mean"][cls]["Dice"]
            dice_by_class[cls].append(dice_value)

    # stats
    dice_mean = {cls: float(np.mean(vals)) for cls, vals in dice_by_class.items()}
    dice_std  = {cls: float(np.std(vals))  for cls, vals in dice_by_class.items()}

    all_results[model_name] = {"dice_mean": dice_mean, "dice_std": dice_std}


# ----- Construction du tableau final -----
rows = []
for model, metrics in all_results.items():
    for cls in ["1", "2", "3", "4"]:
        rows.append({
            "Model": model,
            "Class": cls,
            "Dice Mean": metrics["dice_mean"][cls],
            "Dice Std": metrics["dice_std"][cls]
        })

df = pd.DataFrame(rows).sort_values(["Class", "Model"])
print(df.to_string(index=False))

dice_by_class_models = {}

for model_name, trainer_dir in MODELS.items():
    model_path = os.path.join(BASE_DIR, model_name, trainer_dir)

    # récupérer les Dice par classe
    dice_by_class = {cls: [] for cls in ["1", "2", "3", "4"]}

    for fold in range(5):
        fold_path = os.path.join(model_path, f"fold_{fold}")
        summary = load_summary(fold_path)
        if summary is None:
            continue

        for cls in dice_by_class:
            dice_by_class[cls].append(summary["mean"][cls]["Dice"])

    dice_by_class_models[model_name] = dice_by_class


# --- plot ---
models = list(dice_by_class_models.keys())
classes = ["1", "2", "3", "4"]

fig, axes = plt.subplots(1, 4, figsize=(18, 4), sharey=True)

for idx, cls in enumerate(classes):
    data = [dice_by_class_models[m][cls] for m in models]
    axes[idx].boxplot(data, labels=models)
    axes[idx].set_title(f"Classe {cls}")
    axes[idx].set_ylabel("Dice")

plt.tight_layout()
plt.savefig("tmp.png")


# ======================================================================
# 2) CLASSEMENT DES MODELS
# ======================================================================

# Calcul du Dice moyen global par modèle
ranking = []

for model in models:
    all_values = []
    for cls in classes:
        all_values.extend(dice_by_class_models[model][cls])
    mean_dice = float(np.mean(all_values))
    ranking.append((model, mean_dice))

ranking_df = pd.DataFrame(ranking, columns=["Model", "Mean Dice"])
ranking_df = ranking_df.sort_values("Mean Dice", ascending=False)

print("\n====================")
print("CLASSEMENT GLOBAL")
print("====================")
print(ranking_df.to_string(index=False))


# Classement par classe
rows = []
for cls in classes:
    for model in models:
        mean_cls = np.mean(dice_by_class_models[model][cls])
        rows.append([cls, model, mean_cls])

ranking_per_class = pd.DataFrame(rows, columns=["Class", "Model", "Dice Mean"])
ranking_per_class = ranking_per_class.sort_values(["Class", "Dice Mean"], ascending=[True, False])

print("\n====================")
print("CLASSEMENT PAR CLASSE")
print("====================")
print(ranking_per_class.to_string(index=False))