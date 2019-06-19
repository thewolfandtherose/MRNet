import torch
import pandas as pd

from glob import glob
from PIL import Image

from torch.utils.data import Dataset
from torchvision import transforms


class MRNetDataset(Dataset):
    planes = ['axial', 'coronal', 'sagittal']

    def __init__(self, data_dir, dataset, plane, diagnosis, transform=None):
        self.data_dir = data_dir
        self.dataset = dataset
        self.plane = plane
        self.diagnosis = diagnosis
        self.transform = transform
        self.window = 7

        self.case_paths = sorted(glob(f'{data_dir}/{dataset}/**'))[:100]
        self.labels_df = pd.read_csv(f'{data_dir}/{dataset}_labels.csv')[diagnosis]

    def __len__(self):
        return len(self.case_paths)

    def __getitem__(self, idx):
        case_path = self.case_paths[idx]
        image_paths = sorted(glob(f'{case_path}/{self.plane}/*.png'))

        mid_idx = len(image_paths) // 2
        from_idx = mid_idx - self.window
        to_idx = mid_idx + self.window + 1

        paths = image_paths[from_idx:to_idx]

        data = torch.tensor([])

        for path in paths:
            image = Image.open(path)

            if self.transform is not None:
                image = self.transform(image).unsqueeze(0)

            data = torch.cat((data, image), 0)

        label = torch.tensor([float(self.labels_df.iloc[idx])])
        return (data, label)


def make_datasets(data_dir, plane, diagnosis):
    train_transform = transforms.Compose([
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(45),
        transforms.ToTensor()
    ])

    valid_transform = transforms.Compose([
        transforms.ToTensor()
    ])

    train_dataset = MRNetDataset(data_dir, 'train', plane, diagnosis, transform=train_transform)
    valid_dataset = MRNetDataset(data_dir, 'valid', plane, diagnosis, transform=valid_transform)

    return train_dataset, valid_dataset
