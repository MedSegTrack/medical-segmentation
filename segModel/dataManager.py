import os
import nibabel as nib
import numpy as np
from PIL import Image

class DataManager:
    def __init__(self, target_shape=(240, 240)):
        self.target_shape = target_shape

    def pad_slice(self, slice_2d):
        """
        Pads a 2D slice with black background to make it the target shape.
        Moves non-zero values from the slice into the center of the newly created black image.
        """
        padded_slice = np.zeros(self.target_shape, dtype=slice_2d.dtype)
        x_offset = (self.target_shape[0] - slice_2d.shape[0]) // 2
        y_offset = (self.target_shape[1] - slice_2d.shape[1]) // 2
        padded_slice[x_offset:x_offset + slice_2d.shape[0], y_offset:y_offset + slice_2d.shape[1]] = slice_2d
        return padded_slice

    def normalize_slice(self, slice_2d):
        """
        Normalizes a 2D slice to the range 0-255 for saving as an 8-bit image.
        """
        min_val = slice_2d.min()
        max_val = slice_2d.max()
        if max_val > min_val:
            normalized = 255 * (slice_2d - min_val) / (max_val - min_val)
        else:
            normalized = np.zeros_like(slice_2d)
        return normalized.astype(np.uint8)

    def save_slices(self, data, output_path, scan_name, image_format="jpeg"):
        """
        Save slices of a NIfTI file along all axes in the specified format.
        """

        if data.ndim == 3:
            x_dim, y_dim, z_dim = data.shape
            num_modalities = 1
            data = data[..., np.newaxis]
        elif data.ndim == 4:
            x_dim, y_dim, z_dim, num_modalities = data.shape

        scan_dir = os.path.join(output_path, scan_name)
        os.makedirs(scan_dir, exist_ok=True)

        for modality in range(num_modalities):
            modality_dir = os.path.join(scan_dir, f"modality_{modality + 1}")
            os.makedirs(modality_dir, exist_ok=True)

            scans_x_dir = os.path.join(modality_dir, "scans_x")
            scans_y_dir = os.path.join(modality_dir, "scans_y")
            scans_z_dir = os.path.join(modality_dir, "scans_z")
            os.makedirs(scans_x_dir, exist_ok=True)
            os.makedirs(scans_y_dir, exist_ok=True)
            os.makedirs(scans_z_dir, exist_ok=True)

            for x in range(x_dim):
                slice_x = data[x, :, :, modality]
                if np.any(slice_x):
                    self._save_slice(slice_x, scans_x_dir, x, image_format)

            for y in range(y_dim):
                slice_y = data[:, y, :, modality]
                if np.any(slice_y):
                    self._save_slice(slice_y, scans_y_dir, y, image_format)

            for z in range(z_dim):
                slice_z = data[:, :, z, modality]
                if np.any(slice_z):
                    self._save_slice(slice_z, scans_z_dir, z, image_format)

    def _save_slice(self, slice_data, directory, index, image_format):
        """
        Save a single slice as an image in the specified format.
        """
        normalized = self.normalize_slice(slice_data)
        padded = self.pad_slice(normalized)
        slice_img = Image.fromarray(padded)
        slice_img.save(os.path.join(directory, f"{index}.{image_format}"))

    def process_all_scans(self, data, output_folder, scan_name, image_format="jpeg"):
        """
        Processes all .nii.gz files in the input folder and saves slices to the output folder.
        """

        os.makedirs(output_folder, exist_ok=True)
        self.save_slices(data, output_folder, scan_name, image_format)
