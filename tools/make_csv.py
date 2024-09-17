import sys
import os
import glob
import pandas as pd
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from tools import assert_files


def build_csv(data, filename):
    df = pd.DataFrame(data)

    print(df)


if __name__ == "__main__":
    base_path = cfg.MESO_OUTPUT_PATH
    dico_stacks = assert_files.count_stack(base_path)

    build_csv(dico_stacks, "")