import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
from tools import denoising_2D as denoising
import configuration as cfg


if __name__ == "__main__":

    input_path = cfg.MESO_DATA_PATH
    output_path = cfg.MESO_OUTPUT_PATH
    denoising.denoising_data(input_path, output_path)