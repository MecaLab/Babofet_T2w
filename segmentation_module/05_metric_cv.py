import sys
import os
import json
import numpy as np
import pandas as pd
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