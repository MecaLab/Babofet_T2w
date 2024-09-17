import sys
import os
import glob
import pandas as pd
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from tools import assert_files


def build_csv(dico_stacks, filename):
    df = pd.DataFrame(columns=["subject-ses", "nb_stacks"])

    for subject in dico_stacks.keys():
        for sess_id, nb_stack in dico_stacks[subject].items():
            full_name = f"{subject}-ses_{sess_id}"
            new_row = {"subject": full_name, "nb_stacks": nb_stack}
            df = df.append(new_row, ignore_index=True)

    print(df)


if __name__ == "__main__":
    base_path = cfg.MESO_OUTPUT_PATH
    dico_stacks = assert_files.count_stack(base_path)

    build_csv(dico_stacks, "")
"""
    for name in dico_stack.keys():
        print(name)
        for sess_id, nb_stack in dico_stack[name].items():
            print(f"\t{sess_id} has {nb_stack} stacks")"""