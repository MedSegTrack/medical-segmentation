import unittest
import numpy as np
from model.volume import Volume
from model.slice import Slice

class TestVolume(unittest.TestCase):
    def setUp(self):
        self.data = np.random.rand(5, 5, 3)
        self.axis = 'z'
        self.volume = Volume(self.data, self.axis, 3)

    def test_slice_creation(self):
        for z in range(self.data.shape[2]):
            slice_ = self.volume.get_slice(z)
            self.assertIsInstance(slice_, Slice)
            self.assertEqual(slice_.z_index, z)
            self.assertTrue(np.array_equal(slice_.get_image_as_array(), self.data[:, :, z]))

    def test_get_slices(self):
        slices = [self.volume.get_slice(z) for z in range(self.data.shape[2])]
        self.assertEqual(len(slices), self.data.shape[2])
        for z, slice_ in enumerate(slices):
            self.assertIsInstance(slice_, Slice)
            self.assertEqual(slice_.z_index, z)
            self.assertTrue(np.array_equal(slice_.get_image_as_array(), self.data[:, :, z]))

if __name__ == '__main__':
    unittest.main()