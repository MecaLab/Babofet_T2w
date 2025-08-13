import os
import sys
from typing import Union, List, Tuple
import torch.nn as nn
import torch
from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


class nnUNetTrainer_03Dropout_3000epochs(nnUNetTrainer):

    def __init__(self,
                 plans: dict,
                 configuration: str,
                 fold: int,
                 dataset_json: dict,
                 device: torch.device = torch.device('cuda')):
        super().__init__(plans, configuration, fold, dataset_json, device)
        self.num_epochs = 3000

    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> torch.nn.Module:

        # Vérifier qu'il y a bien un paramètre dropout
        if 'dropout_op_kwargs' not in arch_init_kwargs.keys():
            raise RuntimeError("'dropout_op_kwargs' not found in arch_init_kwargs. "
                               "Ce trainer suppose une architecture nnU-Net classique avec du dropout configuré.")

        new_dropout_rate = 0.3

        if 'dropout_op_kwargs' not in arch_init_kwargs.keys() or arch_init_kwargs['dropout_op_kwargs'] is None:
            arch_init_kwargs['dropout_op_kwargs'] = {'p': new_dropout_rate, 'inplace': True}
        else:
            arch_init_kwargs['dropout_op_kwargs']['p'] = new_dropout_rate

        network = nnUNetTrainer.build_network_architecture(
            architecture_class_name,
            arch_init_kwargs,
            arch_init_kwargs_req_import,
            num_input_channels,
            num_output_channels,
            enable_deep_supervision
        )

        print("\n=== Vérification Dropout ===")
        for name, module in network.named_modules():
            if hasattr(module, 'dropout_op_kwargs'):
                print(f"{name}: dropout p = {module.dropout_op_kwargs['p']}")
        print("===========================\n")

        # Construire le réseau comme d'habitude
        return network


if __name__ == "__main__":
    print("Copying file to appropriate directory")

    current_file_path = os.path.join(cfg.CODE_PATH, "segmentation_module/nnunet_module/"
                                                    "nnUNetTrainer_XDropout_Xepochs.py")
    os.system(f"cp {current_file_path} {cfg.NNUNET_PYTHON_PATH}")
