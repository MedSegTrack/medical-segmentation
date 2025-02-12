import unittest
import numpy as np
from model.slice import Slice
from model.voxel import Voxel

class TestSlice(unittest.TestCase):
    def setUp(self):
        self.data = np.random.rand(5, 5, 3)
        self.z_index = 2
        self.slice = Slice(self.data, self.z_index, 'z')

    def test_voxel_creation(self):
        for x in range(self.data.shape[0]):
            for y in range(self.data.shape[1]):
                voxel = self.slice.get_voxel(x, y)
                self.assertIsInstance(voxel, Voxel)
                self.assertEqual(voxel.x, x)
                self.assertEqual(voxel.y, y)
                self.assertEqual(voxel.z, self.z_index)
                self.assertEqual(voxel.value, self.data[x, y, self.z_index])

    def test_get_image(self):
        self.assertTrue(np.array_equal(self.slice.get_image_as_array(), self.data[:, :, self.z_index]))

if __name__ == '__main__':
    unittest.main()