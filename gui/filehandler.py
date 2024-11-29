import nibabel as nib
import numpy as np

class FileHandler:
    """
    Class to handle the loading of Nifti files and the extraction of slices.
    """
    def __init__(self):
        self.nii_data = None
        self.nii_mask = None
        self.current_slice = {"x": 0, "y": 0, "z": 0}
        self.current_modality_channel = 0


    def load_nifti_file(self, path):
        """
        Load a Nifti file from a given path and store the data in the class attribute `nii_data`.

        Args:
            path (str): Path to the Nifti file to load
        """
        nifti_img = nib.load(path)
        self.nii_data = nifti_img.get_fdata()
        self.current_slice = {"x": self.nii_data.shape[0] // 2, "y": self.nii_data.shape[1] // 2, "z": self.nii_data.shape[2] // 2}
        # If the data is 3D, add a channel dimension
        if len(self.nii_data.shape) == 3:
            self.nii_data = np.expand_dims(self.nii_data, axis=-1)

    def load_nifti_mask(self, path):
        """
        Load a Nifti mask file from a given path and store the data in the class attribute `nii_mask`.

        Args:
            path (str): Path to the Nifti mask file to load
        """
        nifti_mask_img = nib.load(path)
        self.nii_mask = nifti_mask_img.get_fdata()


    def get_slice(self, dimension, index, channel=0):
        """
        Get a slice of the Nifti data along a given dimension.

        Args:
            dimension (str): Dimension along which to extract the slice. Can be "x", "y" or "z"
            index (int): Index of the slice to extract
            channel (int, optional): Channel of the data to extract

        Returns:
            np.ndarray: Slice of the Nifti data
        """
        if self.nii_data is None:
            return None
    
        if dimension == "x":
            if index < self.nii_data.shape[0]:
                return self.nii_data[index, :, :, channel]
        elif dimension == "y":
            if index < self.nii_data.shape[1]:
                return self.nii_data[:, index, :, channel]
        elif dimension == "z":
            if index < self.nii_data.shape[2]:
                return self.nii_data[:, :, index, channel]

        return None

    def get_current_slice_index(self, dimension):
        """
        Get the index of the current slice along a given dimension.

        Args:
            dimension (str): Dimension along which to get the current slice index. Can be "x", "y" or "z"

        Returns:
            int: Index of the current slice along the given dimension
        """
        return self.current_slice.get(dimension, 1)

    def get_mask_slice(self, dimension, index):
        """
        Get a slice of the Nifti mask data along a given dimension.

        Args:
            dimension (str): Dimension along which to extract the slice. Can be "x", "y" or "z"
            index (int): Index of the slice to extract

        Returns:
            np.ndarray: Slice of the Nifti mask data with different colors for each channel
        """
        if self.nii_mask is None:
            return None

        if dimension == "x":
            if index < self.nii_mask.shape[0]:
                mask_slice = self.nii_mask[index, :, :]
        elif dimension == "y":
            if index < self.nii_mask.shape[1]:
                mask_slice = self.nii_mask[:, index, :]
        elif dimension == "z":
            if index < self.nii_mask.shape[2]:
                mask_slice = self.nii_mask[:, :, index]
        else:
            return None

        # Create a colored mask
        colored_mask = np.zeros((*mask_slice.shape, 4))  # RGBA

        # Set colors for different channels
        colored_mask[mask_slice == 1] = [1, 1, 0, 0.5]  # Yellow with 50% opacity
        colored_mask[mask_slice == 2] = [1, 0.65, 0, 0.5]  # Orange with 50% opacity
        colored_mask[mask_slice == 3] = [1, 0, 0, 0.5]  # Red with 50% opacity

        return colored_mask
