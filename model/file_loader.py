import nibabel as nib
import numpy as np
from .nifti import Nifti

class FileLoader:
    def __init__(self, file_path=None):
        self.file_path = file_path
        self.nii_data = None
        self.nifti = None

        if file_path is not None:
            self.load_file()

    def load_file(self):
        self.nii_data = nib.load(self.file_path).get_fdata()
        if len(self.nii_data.shape) == 3:
            self.nii_data = np.expand_dims(self.nii_data, axis=-1)
        modalities = list(range(self.nii_data.shape[3]))
        self.nifti = Nifti(self.nii_data, modalities=modalities)

    def save_file(self, file_path):
        data_shape = self.nifti.shape[:3]
        num_modalities = len(self.nifti.modalities)
        data = np.zeros((*data_shape, num_modalities))
        modality_index = 0
        for volume in self.nifti.get_volumes():
            if volume.axis == 'z':
                for z in range(volume.shape[2]):
                    slice_ = volume.get_slice(z)
                    for x in range(slice_.shape[0]):
                        for y in range(slice_.shape[1]):
                            voxel = slice_.get_voxel(x, y)
                            data[x, y, z, modality_index] = voxel.value
                modality_index += 1
        nifti_img = nib.Nifti1Image(data, affine=np.eye(4))
        nib.save(nifti_img, file_path)