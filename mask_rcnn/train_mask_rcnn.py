import torch
import torch.nn as nn
import torchvision
from torchvision import models
import torch.nn.functional as F
import torchvision.transforms as T
from torchvision import datasets, transforms
from tqdm import tqdm
from torch.utils.data import DataLoader, Dataset, random_split, Subset
from torch.utils.tensorboard import SummaryWriter

from torchvision.transforms.functional import to_pil_image
from torchvision.ops.boxes import masks_to_boxes
from torchvision.utils import draw_bounding_boxes, draw_segmentation_masks

import utils

import torchvision.models.detection as detection
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
import random
from sklearn.model_selection import train_test_split
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat
from torchmetrics.detection.mean_ap import MeanAveragePrecision

import PIL
import nibabel as nib
import os


base_path = "/scratch/lbaptiste/data/dataset/babofet/derivatives"
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

LIST_SUBJECTS = [
    "sub-Aziza_ses-01", "sub-Aziza_ses-05", "sub-Aziza_ses-09" 
    "sub-Fabienne_ses-01", "sub-Fabienne_ses-05", "sub-Fabienne_ses-08", "sub-Fabienne_ses-09",
    "sub-Formule_ses-01", "sub-Formule_ses-05", "sub-Formule_ses-09"
]


def load_nii_file(file_path):
    img = nib.load(file_path)
    img_data = img.get_fdata()
    return img_data


class MRISlicesDataset(Dataset):
    def __init__(self, root_dir, slice_step=1, transforms=None):
        self.root_dir = root_dir
        self.slice_step = slice_step
        self.transforms = transforms

        self.samples = []

        self._load_all()

    def _load_all(self):
        for subject in os.listdir(self.root_dir):
            if subject not in LIST_SUBJECTS:
                continue

            print(subject)
            subject_path = os.path.join(self.root_dir, subject)

            anats_path = os.path.join(subject_path, "denoising")
            bms_path = os.path.join(subject_path, "manual_masks")

            for file in os.listdir(anats_path):
                bm_filename = file.replace(".nii", "_mask.nii.gz")

                anat_path = os.path.join(anats_path, file)
                bm_path = os.path.join(bms_path, bm_filename)

                if not os.path.exists(bm_path):
                    continue

                img = load_nii_file(anat_path)
                if img.shape[2] < 20:
                    continue
                for i in range(0, img.shape[2], self.slice_step):
                    self.samples.append((anat_path, bm_path, i, subject))

        print("Fin chargement des donnees")

    """def _load_all(self):
        for subject in os.listdir(self.root_dir):
            if subject not in LIST_SUBJECTS:
                continue
            subject_path = os.path.join(self.root_dir, subject)
            for session in os.listdir(subject_path):
                if session not in LIST_SESSION:
                    continue
                anats_path = os.path.join(subject_path, session, "stacks")
                bms_path = os.path.join(subject_path, session, "brainmask")

                for file in os.listdir(anats_path):
                    bm_filename = file.replace(".nii", "_mask.nii.gz")

                    anat_path = os.path.join(anats_path, file)
                    bm_path = os.path.join(bms_path, bm_filename)

                    if not os.path.exists(bm_path):
                        continue

                    img = load_nii_file(anat_path)
                    if img.shape[2] < 20:
                        continue
                    for i in range(0, img.shape[2], self.slice_step):
                        self.samples.append((anat_path, bm_path, i, subject))

        print("Fin chargement des donnees")"""

    def __getitem__(self, idx):
        anat_path, bm_path, slice_idx, _ = self.samples[idx]

        anat_img = load_nii_file(anat_path)
        bm_img = load_nii_file(bm_path)

        img_slice = anat_img[:, :, slice_idx]
        mask_slice = bm_img[:, :, slice_idx]

        # Normalisation
        img_slice = (img_slice - img_slice.min()) / (img_slice.max() - img_slice.min() + 1e-8)
        img_tensor = torch.tensor(img_slice, dtype=torch.float32).unsqueeze(0)  # [1, H, W]

        mask_tensor = torch.tensor(mask_slice > 0, dtype=torch.uint8)

        obj_ids = torch.unique(mask_tensor)[1:]  # remove bg
        num_objects = len(obj_ids)

        masks = (mask_tensor == obj_ids[:, None, None]).to(dtype=torch.uint8)

        boxes = masks_to_boxes(masks)

        labels = torch.ones((num_objects,), dtype=torch.int64)
        img_id = idx
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        iscrowd = torch.zeros((num_objects,), dtype=torch.int64)

        target = {
            "boxes": boxes,
            "masks": masks,
            "labels": labels,
            "image_id": img_id,
            "area": area,
            "iscrowd": iscrowd
        }

        if self.transforms:
            img_tensor, target = self.transforms(img_tensor, target)

        return img_tensor, target

    def __len__(self):
        return len(self.samples)


def split_dataset_by_subject(dataset, test_size=0.1, val_size=0.2, random_state=42):
    # Organiser les indices par subject
    subject_to_indices = defaultdict(list)
    for idx, sample in enumerate(dataset.samples):
        subject = sample[3]  # on a ajouté subject dans les samples
        subject_to_indices[subject].append(idx)

    all_subjects = list(subject_to_indices.keys())

    # Split test
    train_val_subjects, test_subjects = train_test_split(
        all_subjects, test_size=test_size, random_state=random_state
    )

    # Split val depuis train_val
    train_subjects, val_subjects = train_test_split(
        train_val_subjects, test_size=val_size / (1 - test_size), random_state=random_state
    )

    def indices_from_subjects(subject_list):
        return [idx for s in subject_list for idx in subject_to_indices[s]]

    train_indices = indices_from_subjects(train_subjects)
    val_indices = indices_from_subjects(val_subjects)
    test_indices = indices_from_subjects(test_subjects)

    return train_indices, val_indices, test_indices


def collate_fn(batch):
    images, targets = zip(*batch)
    filtered_targets = []
    for target in targets:
        boxes = target["boxes"]
        labels = target["labels"]
        masks = target["masks"]
        if len(boxes) != 0:
            filtered_targets.append({
                'boxes': torch.tensor(boxes, dtype=torch.float32),
                'labels': torch.tensor(labels, dtype=torch.int64),
                'masks': torch.tensor(masks, dtype=torch.uint8),
            })
        else:
            # Pour éviter des batches vides (Faster R-CNN n'aime pas ça)
            filtered_targets.append({
                'boxes': torch.zeros((0, 4), dtype=torch.float32),
                'labels': torch.zeros((0,), dtype=torch.int64),
                'masks': torch.zeros((0, 1, 1), dtype=torch.uint8),

            })
    return images, filtered_targets


def get_model(num_classes):
    model = detection.maskrcnn_resnet50_fpn(pretrained=True)

    # Get the number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # Replace pretrained head with new one
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layers = 32

    model.roi_heads.mask_predictor = MaskRCNNPredictor(
        in_features_mask,
        hidden_layers,
        num_classes
    )
    return model


writer = SummaryWriter(log_dir='runs/brain_seg')


def train_one_epoch(model, data_loader, device, optimizer, print_freq, epoch, scaler=None):
    model.train()
    metric_logger = utils.MetricLogger(delimiter="  ")
    metric_logger.add_meter("lr", utils.SmoothedValue(window_size=1, fmt="{value:.6f}"))
    header = f"Training Epoch {epoch}:"
    model.to(device)

    with tqdm(data_loader, desc=header) as tq:
        for i, (images, targets) in enumerate(tq):
            images = [img.to(device) for img in images]
            targets = [{k: v.to(device) for k, v in t.items()} for t in targets]

            with torch.cuda.amp.autocast(enabled=scaler is not None):
                loss_dict = model(images, targets)
                losses = sum(loss for loss in loss_dict.values())

            loss_value = losses.item()

            optimizer.zero_grad()
            if scaler is not None:
                scaler.scale(losses).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                losses.backward()
                optimizer.step()

            metric_logger.update(loss=losses, **loss_dict)
            metric_logger.update(lr=optimizer.param_groups[0]["lr"])

            # Update tqdm postfix to display loss on the progress bar
            tq.set_postfix(loss=losses.item(), lr=optimizer.param_groups[0]["lr"])

            # Log losses to TensorBoard
            writer.add_scalar('Loss/train', losses.item(), epoch * len(data_loader) + i)
            for k, v in loss_dict.items():
                writer.add_scalar(f'Loss/train_{k}', v.item(), epoch * len(data_loader) + i)
            break

    print(f"Average Loss: {metric_logger.meters['loss'].global_avg:.4f}")
    writer.add_scalar('Loss/avg_train', metric_logger.meters['loss'].global_avg, epoch)


def evaluate(model, data_loader, device, epoch, save_dir):
    model.eval()
    metric = MeanAveragePrecision(iou_type="bbox")

    metric = metric.to(device)
    total_iou = 0
    total_detections = 0
    header = "Validation:"
    total_steps = len(data_loader)
    samples = []

    with torch.no_grad(), tqdm(total=total_steps, desc=header) as progress_bar:
        for i, (images, targets) in enumerate(data_loader):
            images = [img.to(device) for img in images]
            targets = [{k: v.to(device) for k, v in t.items()} for t in targets]
            outputs = model(images)

            # Convert outputs for torchmetrics
            preds = [
                {"boxes": out["boxes"].to(device), "scores": out["scores"].to(device), "labels": out["labels"].to(device)}
                for out in outputs
            ]
            targs = [
                {"boxes": tgt["boxes"].to(device), "labels": tgt["labels"].to(device)}
                for tgt in targets
            ]

            for j, pred in enumerate(preds):
                print(
                    f"Prediction {j} - boxes device: {pred['boxes'].device}, scores device: {pred['scores'].device}, labels device: {pred['labels'].device}")
            for j, targ in enumerate(targs):
                print(f"Target {j} - boxes device: {targ['boxes'].device}, labels device: {targ['labels'].device}")

            # Update metric for mAP calculation
            metric.update(preds, targs)

            progress_bar.update(1)
            break 

    results = metric.compute()
    print("mAP results:")
    print(results)

    # Log mAP to TensorBoard
    for k, v in results.items():
        if v.numel() == 1:  # Single element tensor
            writer.add_scalar(f'mAP/{k}', v.item(), epoch)
        else:  # Multi-element tensor, log each element separately
            for idx, value in enumerate(v):
                writer.add_scalar(f'mAP/{k}_{idx}', value.item(), epoch)
    return results


def train_model(num_epochs):
    best_map = -float('inf')  # Training loop
    for epoch in range(num_epochs):
        # Memory Cleanup.
        torch.cuda.empty_cache()
        # train for one epoch, printing every 10 iterations
        train_one_epoch(model, train_loader, device, optimizer, print_freq=50, epoch=epoch, scaler=scaler)
        # evaluate on the validation dataset
        results = evaluate(model, val_loader, device, epoch, save_dir='predictions')

        # Save the model checkpoint if it's the best mAP
        current_map = results['map'].item()
        if current_map > best_map:
            best_map = current_map
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_map': best_map,
                'scaler': scaler.state_dict() if scaler is not None else None
            }, os.path.join(save_dir, f'best_model_checkpoint_epoch_{epoch}.pth'))
            best_epoch_model = epoch

    print("That's it!")
    writer.close()
    return best_epoch_model


def load_model(checkpoint_weight, device):
    model = get_model(2)
    checkpoint = torch.load(checkpoint_weight, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()

    print(f"Loaded {checkpoint_weight}")
    return model

custom_ds = MRISlicesDataset(base_path)

train_idx, val_idx, test_idx = split_dataset_by_subject(custom_ds)

train_dataset = Subset(custom_ds, train_idx)
val_dataset = Subset(custom_ds, val_idx)
test_dataset = Subset(custom_ds, test_idx)

print(len(train_dataset), len(val_dataset), len(test_dataset))

# Exemple d’utilisation
train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True, collate_fn=collate_fn)
val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False, collate_fn=collate_fn)
test_loader = DataLoader(test_dataset, batch_size=8, shuffle=False, collate_fn=collate_fn)

num_classes = 1 + 1  # background + class, ie brain
model = get_model(num_classes).to(device)

num_epochs = 10
params = [p for p in model.parameters() if p.requires_grad]
optimizer = torch.optim.SGD(params, lr=0.0005, momentum=0.9, weight_decay=0.0005)
scaler = torch.cuda.amp.GradScaler()

save_dir = "checkpoints"
os.makedirs(save_dir, exist_ok=True)

best_epoch_model = train_model(num_epochs)

checkpoint_weight = os.path.join(save_dir, f"best_model_checkpoint_epoch_{best_epoch_model}.pth")

model = load_model(checkpoint_weight, device)

print("OK")

