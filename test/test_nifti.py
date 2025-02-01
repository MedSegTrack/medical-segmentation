import unittest
import numpy as np
from model.file_loader import FileLoader
from model.nifti import Nifti
from model.volume import Volume

import matplotlib.pyplot as plt
import os

class TestNifti(unittest.TestCase):
    def setUp(self):
        self.data = np.random.rand(240, 240, 155, 2)
        self.modalities = [0, 1]
        self.nifti = Nifti(self.data, self.modalities)

    def test_volume_creation(self):
        for modality_index in range(self.data.shape[3]):
            volume = self.nifti.get_volume(modality_index)
            self.assertIsInstance(volume, Volume)
            self.assertEqual(volume.shape, self.data[:, :, :, modality_index].shape[:3])

    def test_get_volumes(self):
        volumes = self.nifti.get_volumes()
        self.assertEqual(len(volumes), self.data.shape[3] * 3)
        for modality_index in range(self.data.shape[3]):
            volume = volumes[modality_index]
            self.assertIsInstance(volume, Volume)
            self.assertEqual(volume.shape, self.data[:, :, :, modality_index].shape[:3])

    def test_volume_iteration(self):
        for volume in self.nifti.get_volumes():
            if volume.axis == 'x':
                for z_index in range(240):
                    slice_ = volume.get_slice(z_index)
                    self.assertEqual(slice_.shape, (240, 155))
            elif volume.axis == 'y':
                for z_index in range(240):
                    slice_ = volume.get_slice(z_index)
                    self.assertEqual(slice_.shape, (240, 155))
            elif volume.axis == 'z':
                for z_index in range(155):
                    slice_ = volume.get_slice(z_index)
                    self.assertEqual(slice_.shape, (240, 240))

if __name__ == '__main__':
    unittest.main()