import unittest
import numpy as np
from model.voxel import Voxel
from model.slice import Slice

class TestVoxel(unittest.TestCase):
    def setUp(self):
        self.data = np.random.rand(5, 5, 3)
        self.z_index = 2
        self.slice = Slice(self.data, self.z_index, 'z')

    def test_voxel_dynamic_creation(self):
        voxel = self.slice.get_voxel(1, 2)
        self.assertEqual(voxel.value, self.data[1, 2, self.z_index])
        self.data[1, 2, self.z_index] = 10.0
        self.assertEqual(voxel.value, 10.0)

    def test_voxel_value_change(self):
        voxel = self.slice.get_voxel(1, 2)
        voxel.value = 20.0
        self.assertEqual(self.data[1, 2, self.z_index], 20.0)

    def test_voxel_equality(self):
        voxel1 = Voxel(self.data, 1, 2, self.z_index)
        voxel2 = Voxel(self.data, 1, 2, self.z_index)
        voxel3 = Voxel(self.data, 1, 2, 1)
        self.assertEqual(voxel1, voxel2)
        self.assertNotEqual(voxel1, voxel3)

    def test_voxel_repr(self):
        voxel = Voxel(self.data, 1, 2, self.z_index)
        self.assertEqual(repr(voxel), f"Voxel(x=1, y=2, z={self.z_index}, value={self.data[1, 2, self.z_index]})")

if __name__ == '__main__':
    unittest.main()