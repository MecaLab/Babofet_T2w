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


def load_summary_json(path):
    """Charge summary.json dans un fold."""
    summary_path = os.path.join(path, "summary.json")
    if not os.path.isfile(summary_path):
        print(f"[WARNING] summary.json not found: {summary_path}")
        return None
    with open(summary_path, "r") as f:
        return json.load(f)


all_results = {}

for model_name, trainer_dir in MODELS.items():

    model_path = os.path.join(BASE_DIR, model_name, trainer_dir)

    dice_by_fold = {}
    hd95_by_fold = {}

    for fold in range(5):
        fold_dir = os.path.join(model_path, f"fold_{fold}")
        summary = load_summary_json(fold_dir)
        if summary is None:
            continue

        # nnUNet v2: results -> mean -> metrics
        dice = summary["results"]["Dice"]
        hd95 = summary["results"].get("HD95", {})

        # accumulate Dice
        for cls, value in dice.items():
            dice_by_fold.setdefault(cls, []).append(value)

        # accumulate HD95
        for cls, value in hd95.items():
            hd95_by_fold.setdefault(cls, []).append(value)

    # compute statistics
    dice_mean = {cls: np.mean(vals) for cls, vals in dice_by_fold.items()}
    dice_std = {cls: np.std(vals) for cls, vals in dice_by_fold.items()}

    hd95_mean = {cls: np.mean(vals) for cls, vals in hd95_by_fold.items()} if hd95_by_fold else {}
    hd95_std = {cls: np.std(vals) for cls, vals in hd95_by_fold.items()} if hd95_by_fold else {}

    all_results[model_name] = {
        "dice_mean": dice_mean,
        "dice_std": dice_std,
        "hd95_mean": hd95_mean,
        "hd95_std": hd95_std
    }


# ---------- CONSTRUCTION DU TABLEAU FINAL ----------
rows = []
for model, metrics in all_results.items():
    for cls in metrics["dice_mean"]:
        rows.append({
            "Model": model,
            "Class": cls,
            "Dice Mean": metrics["dice_mean"][cls],
            "Dice Std": metrics["dice_std"][cls],
            "HD95 Mean": metrics["hd95_mean"].get(cls, None),
            "HD95 Std": metrics["hd95_std"].get(cls, None)
        })

df = pd.DataFrame(rows)
print(df)

df = df.sort_values(by=["Class", "Model"])

print("\n===== COMPARAISON DES MODELS nnUNet =====\n")
print(df.to_string(index=False))
