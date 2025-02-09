import os
import numpy as np
from PIL import Image

class NiftiToImageConverter:
    """Converts NIfTI data to image files for SAM2 processing."""
    
    def __init__(self, target_shape=(240, 240)):
        self.target_shape = target_shape
        
    def convert_volume(self, data: np.ndarray, output_dir: str, axis: str = 'z') -> str:
        """Convert volume data to image sequence along specified axis.
        
        Args:
            data: Volume data (3D or 4D array)
            output_dir: Directory to save images
            axis: Axis along which to slice ('x', 'y', or 'z')
            
        Returns:
            str: Path to directory containing image sequence
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Handle 4D data (multiple modalities)
        if data.ndim == 4:
            data = data[..., 0]  # Take first modality by default
            
        if axis == 'z':
            slices = [data[:, :, i] for i in range(data.shape[2])]
        elif axis == 'y':
            slices = [data[:, i, :] for i in range(data.shape[1])]
        elif axis == 'x':
            slices = [data[i, :, :] for i in range(data.shape[0])]
            
        # Save each slice as image
        for idx, slice_data in enumerate(slices):
            normalized = self._normalize_slice(slice_data)
            padded = self._pad_slice(normalized)
            
            rotated = np.rot90(padded, k=1)

            image = Image.fromarray(rotated)
            image.save(os.path.join(output_dir, f"{idx:04d}.jpeg"))
            
        return output_dir
    
    def _normalize_slice(self, slice_data: np.ndarray) -> np.ndarray:
        """Normalize slice data to 0-255 range."""
        min_val = slice_data.min()
        max_val = slice_data.max()
        
        if max_val > min_val:
            normalized = 255 * (slice_data - min_val) / (max_val - min_val)
        else:
            normalized = np.zeros_like(slice_data)
            
        return normalized.astype(np.uint8)
    
    def _pad_slice(self, slice_data: np.ndarray) -> np.ndarray:
        """Pad slice to target shape."""
        if slice_data.shape == self.target_shape:
            return slice_data
            
        padded = np.zeros(self.target_shape, dtype=slice_data.dtype)
        x_offset = (self.target_shape[0] - slice_data.shape[0]) // 2
        y_offset = (self.target_shape[1] - slice_data.shape[1]) // 2
        
        padded[x_offset:x_offset + slice_data.shape[0],
               y_offset:y_offset + slice_data.shape[1]] = slice_data
        
        return padded