import numpy as np
import os
from typing import Dict, Optional
from model.file_loader import FileLoader
from model.nifti import Nifti
from config import CONFIG
from .data_converter import NiftiToImageConverter
from .data_analyzer import DataAnalyzer


class DataManager:
    """Manages data access and file handlers for the application."""

    def __init__(self):
        self.image_loader = None
        self.mask_loader = None
        self.image = None
        self.mask = None
        self.converted_paths: Dict[str, str] = {}
        self.converter = NiftiToImageConverter()
        self.analyzer = DataAnalyzer(self)

    def load_image(self, file_path):
        """Load a NIfTI image file.

        Args:
            file_path (str): Path to the NIfTI file
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.image_loader = FileLoader(file_path)
            self.image = self.image_loader.nifti
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False

    def load_mask(self, file_path):
        """Load a NIfTI mask file.

        Args:
            file_path (str): Path to the NIfTI mask file
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.mask_loader = FileLoader(file_path)
            self.mask = self.mask_loader.nifti
            return True
        except Exception as e:
            print(f"Error loading mask: {e}")
            return False

    def get_image_data(self):
        """Get the current image data.

        Returns:
            Nifti: The current image data
        """
        return self.image

    def get_mask_data(self):
        """Get the current mask data.

        Returns:
            Nifti: The current mask data
        """
        return self.mask

    def get_image_slice(self, dimension, modality_channel, slice_index, is_mask=False):
        """
        Get the image slice for the given dimension, modality channel, and slice index.

        Args:
            dimension (str): The dimension to get the slice from ("x", "y", or "z").
            modality_channel (int): The modality channel index.
            slice_index (int): The index of the slice.
            is_mask (bool): Whether to get the slice from the mask data.

        Returns:
            Slice object if successful.

        Raises:
            ValueError: If any required data is missing.
        """
        data = self.get_mask_data() if is_mask else self.get_image_data()
        if data is None:
            raise ValueError(
                "Data retrieval failed. Ensure image or mask data is available."
            )

        volume = data.get_volume(dimension, 0 if is_mask else modality_channel)
        if volume is None:
            raise ValueError(
                f"Failed to retrieve volume for dimension '{dimension}' and modality channel '{modality_channel}'."
            )

        return volume.get_slice(slice_index)

    def save_image(self, file_path):
        """Save the current image to a file.

        Args:
            file_path (str): Path to save the file
        Returns:
            bool: True if successful, False otherwise
        """
        if self.image_loader:
            try:
                self.image_loader.save_file(file_path)
                return True
            except Exception as e:
                print(f"Error saving image: {e}")
        return False

    def save_mask(self, file_path):
        """Save the current mask to a file.

        Args:
            file_path (str): Path to save the file
        Returns:
            bool: True if successful, False otherwise
        """
        if self.mask_loader:
            try:
                self.mask_loader.save_file(file_path)
                return True
            except Exception as e:
                print(f"Error saving mask: {e}")
        return False

    def prepare_for_segmentation(
        self, axis: str = "z", modality: int = 0
    ) -> Optional[str]:
        """Convert volume data for segmentation.

        Args:
            axis: Axis to slice along ('x', 'y', 'z')
            modality: Index of modality to use (default: 0)

        Returns:
            Optional[str]: Path to converted images directory or None if failed
        """
        if not self.image_loader:
            return None

        # Verify modality index is valid
        if modality >= self.image.shape[-1]:
            print(f"Invalid modality index {modality}. Using default (0)")
            modality = 0

        output_dir = os.path.join(
            CONFIG["temp_dir"],
            f"scan_{os.path.basename(self.image_loader.file_path)}_{axis}_mod{modality}/",
        )

        try:
            path = self.converter.convert_volume(
                self.image_loader.nii_data, output_dir, axis, modality=modality
            )
            self.converted_paths[axis] = path
            return path
        except Exception as e:
            print(f"Error converting volume: {e}")
            return None

    def create_mask_from_segmentation(
        self, masks: Dict[str, np.ndarray], dimension: str
    ) -> bool:
        """Convert segmentation masks to NIfTI structure.

        Args:
            masks: Dictionary of masks from segmentation
            dimension: Axis along which masks were generated ('x','y','z')

        Returns:
            bool: Success status
        """
        if not self.image:
            return False

        # Get original image shape
        orig_shape = self.image.shape[:3]

        # Create empty 4D array matching image dimensions
        # Adding 4th dimension for potential multiple labels
        mask_data = np.zeros((*orig_shape, 1), dtype=np.float32)

        # Fill the volume with mask data
        for key, mask in masks.items():
            dim, idx = key.split("_")
            idx = int(idx)

            mask = np.squeeze(mask)

            # Rotate mask by -90 degrees before inserting
            rotated_mask = np.rot90(mask, k=-1)

            if dimension == "z":
                mask_data[:, :, idx, 0] = rotated_mask
            elif dimension == "y":
                mask_data[:, idx, :, 0] = rotated_mask
            elif dimension == "x":
                mask_data[idx, :, :, 0] = rotated_mask

        # Create new FileLoader instance
        self.mask_loader = FileLoader()
        self.mask_loader.nii_data = mask_data
        self.mask = Nifti(mask_data, modalities=[0])
        self.mask_loader.nifti = self.mask

        return True

    def analyze_current_mask(self) -> Dict[str, str]:
        """Analyze current mask and return formatted results.

        Returns:
            Dict[str, str]: Formatted analysis results or empty dict if no mask
        """
        if not self.mask:
            return {}

        self.analyzer.analyze_mask()
        return self.analyzer.get_formatted_results()
