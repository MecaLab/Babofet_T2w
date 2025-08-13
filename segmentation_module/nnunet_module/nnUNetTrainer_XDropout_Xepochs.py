import os
import sys
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

    def build_network_architecture(self, configuration_manager, plans, dataset_json, configuration_name, fold, **kwargs):
        # On construit le réseau normalement
        network = super().build_network_architecture(configuration_manager, plans, dataset_json, configuration_name, fold, **kwargs)

        new_dropout_rate = 0.3
        for name, module in network.named_modules():
            if hasattr(module, 'dropout_op_kwargs'):
                module.dropout_op_kwargs['p'] = new_dropout_rate

        return network

if __name__ == "__main__":
    print("Copying file to appropriate directory")

    current_file_path = os.path.join(cfg.CODE_PATH, "segmentation_module/nnunet_module/"
                                                    "nnUNetTrainer_XDropout_Xepochs.py")
    os.system(f"cp {current_file_path} {cfg.NNUNET_PYTHON_PATH}")
