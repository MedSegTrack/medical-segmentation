import unittest
import os
import numpy as np
import nibabel as nib

from model.file_loader import FileLoader
from model.nifti import Nifti

class TestFileLoader(unittest.TestCase):
    def setUp(self):
        self.test_file_path = "test.nii"
        data = np.random.rand(240, 240, 155, 4)
        nifti_img = nib.Nifti1Image(data, affine=np.eye(4))
        nib.save(nifti_img, self.test_file_path)
        self.save_img_file_path = "saved_test_img.nii"
        self.save_mask_file_path = "saved_test_mask.nii"

    def tearDown(self):
        os.remove(self.test_file_path)
        if os.path.exists(self.save_img_file_path):
            os.remove(self.save_img_file_path)
        if os.path.exists(self.save_mask_file_path):
            os.remove(self.save_mask_file_path)

    def test_load_img_file(self):
        file_loader = FileLoader(self.test_file_path)
        self.assertIsNotNone(file_loader.nii_data)
        self.assertEqual(file_loader.nii_data.shape, (240, 240, 155, 4))
        self.assertIsInstance(file_loader.nifti, Nifti)
        self.assertEqual(len(file_loader.nifti.get_volumes()), 12)

    def test_save_img_file(self):
        file_loader = FileLoader(self.test_file_path)
        file_loader.save_file(self.save_img_file_path)
        
        # Load the saved file and check its contents
        saved_nifti_img = nib.load(self.save_img_file_path)
        saved_data = saved_nifti_img.get_fdata()
        output_data = nib.load(self.test_file_path).get_fdata()
        self.assertEqual(saved_data.shape, (240, 240, 155, 4))
        self.assertTrue(np.array_equal(saved_data, output_data))

    def test_save_mask_file(self):
        file_loader = FileLoader(self.test_file_path)
        file_loader.save_file(self.save_mask_file_path)
        
        # Load the saved file and check its contents
        saved_nifti_img = nib.load(self.save_mask_file_path)
        saved_data = saved_nifti_img.get_fdata()
        output_data = nib.load(self.test_file_path).get_fdata()
        self.assertEqual(saved_data.shape, (240, 240, 155, 4))
        self.assertTrue(np.array_equal(saved_data, output_data))

if __name__ == '__main__':
    unittest.main()