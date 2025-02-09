import numpy as np
import os
from typing import Dict, Optional, Tuple
from model.file_loader import FileLoader
from model.nifti import Nifti
from config import CONFIG
from .data_converter import NiftiToImageConverter

class DataManager:
    """Manages data access and file handlers for the application."""

    def __init__(self):
        self.image_loader = None
        self.mask_loader = None
        self.image = None
        self.mask = None
        self.converted_paths: Dict[str, str] = {}
        self.converter = NiftiToImageConverter()

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
            Slice object if successful, None otherwise
        """
        data = self.get_mask_data() if is_mask else self.get_image_data()
        if data is None:
            return None
        if is_mask:
            modality_channel = 0
        volume = data.get_volume(dimension, modality_channel)
        if volume is None:
            return None
        slice_obj = volume.get_slice(slice_index)
        return slice_obj

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

    def prepare_for_segmentation(self, axis: str = 'z') -> Optional[str]:
        """Convert volume data for segmentation."""
        if not self.image_loader:
            return None
            
        output_dir = os.path.join(
            CONFIG['temp_dir'],
            f"scan_{os.path.basename(self.image_loader.file_path)}_{axis}/"
        )
        
        try:
            path = self.converter.convert_volume(
                self.image_loader.nii_data,
                output_dir,
                axis
            )
            self.converted_paths[axis] = path
            return path
        except Exception as e:
            print(f"Error converting volume: {e}")
            return None