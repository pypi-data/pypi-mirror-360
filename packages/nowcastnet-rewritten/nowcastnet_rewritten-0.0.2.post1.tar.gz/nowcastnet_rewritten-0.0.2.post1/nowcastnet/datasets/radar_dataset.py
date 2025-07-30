import os

import numpy as np
import cv2 as cv
from torch.utils.data import Dataset


class RadarDataset(Dataset):
    def __init__(self, dataset_config: dict):
        super().__init__()
        self.input_data_type = dataset_config['input_data_type']
        self.output_data_type = dataset_config['output_data_type']

        self.image_width = dataset_config['image_width']
        self.image_height = dataset_config['image_height']
        # ensure the frames' height and width are limited
        assert self.image_height <= 1024 and self.image_width <= 1024

        self.total_length = dataset_config['total_length']
        self.input_length = dataset_config['input_length']
        self.dataset_path = dataset_config['dataset_path']

        self.sample_list = self._build_sample_list()

    def _build_sample_list(self):
        # each sample in sample_list is a list containing paths to its revelent frames
        sample_list = []
        sample_dirs = os.listdir(self.dataset_path)
        for sample_dir in sample_dirs:
            # each case_dir contains 29 frames
            frame_paths = [os.path.join(
                self.dataset_path, sample_dir, f'{sample_dir}-{str(i).zfill(2)}.png') for i in range(29)]
            sample_list.append(frame_paths)

        return sample_list

    def _load_frames(self, sample_idx) -> np.ndarray:
        frames = []
        frame_paths = self.sample_list[sample_idx]
        # load revelent frames for this sample
        for frame_path in frame_paths:
            frame: np.ndarray = cv.imread(frame_path, cv.IMREAD_UNCHANGED)
            frames.append(np.expand_dims(frame, axis=0))
        sample = np.concatenate(frames, axis=0).astype(
            self.input_data_type) / 10 - 3

        assert sample.shape[1] == self.image_height and sample.shape[2] == self.image_width

        return sample

    def __getitem__(self, sample_idx) -> np.ndarray:
        sample = self._load_frames(sample_idx)
        # extract the latest self.total_length frames
        sample = sample[-self.total_length:]

        # mask = np.ones_like(sample)
        # mask[sample < 0] = 0

        sample = np.clip(sample, a_min=0, a_max=128)
        # sample = np.stack((sample, mask), axis=-1)

        return sample[:self.input_length], sample[self.input_length:]

    def __len__(self):
        return len(self.sample_list)
