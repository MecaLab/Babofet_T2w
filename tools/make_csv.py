import sys
import os
import glob
import pandas as pd
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from tools import assert_files


if __name__ == "__main__":
    base_path = cfg.MESO_OUTPUT_PATH
    dico_stacks = assert_files.count_stack(base_path)

    for name in dico_stacks.keys():
        print(name)
        for sess_id, nb_stack in dico_stacks[name].items():
            print(f"\t{sess_id} has {nb_stack} stacks")