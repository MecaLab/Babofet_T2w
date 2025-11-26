import json
import os
import sys
import numpy as np
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

def verify_nnunet_channels(dataset_id="001"):
    """Vérifie que tous les canaux sont correctement pris en compte."""

    base_path = os.path.join(cfg.NNUNET_PREPROCESSED_PATH, f"Dataset{dataset_id}_tmp_longi")

    print("=" * 60)
    print("VÉRIFICATION DES CANAUX nnUNet")
    print("=" * 60)

    # 1. Vérifier dataset_fingerprint.json
    fingerprint_path = os.path.join(base_path, "dataset_fingerprint.json")
    if fingerprint_path.exists():
        with open(fingerprint_path) as f:
            fingerprint = json.load(f)

        num_channels = fingerprint.get("num_channels", 0)
        print(f"\n✓ Nombre de canaux détectés: {num_channels}")

        if num_channels != 3:
            print(f"  ⚠️  ATTENTION: Attendu 3 canaux, trouvé {num_channels}")
        else:
            print(f"  ✓ Correct ! 3 canaux comme attendu")

        print(f"\n  Noms des canaux:")
        for idx, name in fingerprint.get("channel_names", {}).items():
            print(f"    Canal {idx}: {name}")

        print(f"\n  Propriétés d'intensité:")
        for idx, props in enumerate(fingerprint.get("intensityproperties", [])):
            print(f"    Canal {idx}:")
            print(f"      - Mean: {props.get('mean', 'N/A'):.2f}")
            print(f"      - Std: {props.get('std', 'N/A'):.2f}")
            print(f"      - Min: {props.get('percentile_00_5', 'N/A')}")
            print(f"      - Max: {props.get('percentile_99_5', 'N/A')}")
    else:
        print("❌ dataset_fingerprint.json non trouvé")
        return

    # 2. Vérifier les plans
    plans_path = os.path.join(base_path, "nnUNetPlans.json")
    if plans_path.exists():
        with open(plans_path) as f:
            plans = json.load(f)

        print(f"\n✓ Plans trouvés")
        configurations = plans.get("configurations", {})
        print(f"  Configurations disponibles: {list(configurations.keys())}")

        # Vérifier la normalisation
        for config_name, config in configurations.items():
            print(f"\n  Configuration: {config_name}")
            norm_schemes = config.get("normalization_schemes", [])
            print(f"    Schémas de normalisation: {norm_schemes}")
            if len(norm_schemes) != 3:
                print(f"    ⚠️  ATTENTION: {len(norm_schemes)} schémas, attendu 3")

    # 3. Vérifier un fichier prétraité
    print(f"\n" + "=" * 60)
    print("VÉRIFICATION D'UN FICHIER PRÉTRAITÉ")
    print("=" * 60)

    preprocessed_dirs = list(base_path.glob("nnUNetPlans_*"))
    if preprocessed_dirs:
        preprocessed_dir = preprocessed_dirs[0]
        print(f"\nDossier: {preprocessed_dir.name}")

        npz_files = list(preprocessed_dir.glob("*.npz"))
        if npz_files:
            sample_file = npz_files[0]
            print(f"Fichier exemple: {sample_file.name}")

            data = np.load(sample_file)
            print(f"\nContenu du .npz:")
            for key in data.files:
                arr = data[key]
                print(f"  {key}: shape = {arr.shape}, dtype = {arr.dtype}")

                if key == 'data':
                    num_channels_data = arr.shape[0]
                    if num_channels_data != 3:
                        print(f"    ⚠️  ATTENTION: {num_channels_data} canaux dans data, attendu 3")
                    else:
                        print(f"    ✓ 3 canaux confirmés dans les données prétraitées")

                    # Stats par canal
                    print(f"\n    Statistiques par canal:")
                    for ch in range(arr.shape[0]):
                        print(f"      Canal {ch}: min={arr[ch].min():.2f}, "
                              f"max={arr[ch].max():.2f}, "
                              f"mean={arr[ch].mean():.2f}, "
                              f"std={arr[ch].std():.2f}")
        else:
            print("  ❌ Aucun fichier .npz trouvé")
    else:
        print("\n❌ Aucun dossier preprocessed trouvé")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    verify_nnunet_channels()