import numpy as np
from typing import Dict, Optional, Tuple
from scipy import ndimage
from skimage import measure

class DataAnalyzer:
    """Analyzes mask properties and provides statistical measurements."""
    
    def __init__(self, data_manager):
        """Initialize analyzer with data manager reference.
        
        Args:
            data_manager: Reference to DataManager instance
        """
        self.data_manager = data_manager
        self._reset_measurements()
        
    def _reset_measurements(self):
        """Reset all measurements to initial state."""
        self.measurements = {
            'volume': 0,  # in voxels
            'surface_area': 0,  # in voxel faces
            'centroid': None,  # (x,y,z) coordinates
            'bbox': None,  # bounding box (min_x, min_y, min_z, max_x, max_y, max_z)
            'dimensions': None,  # (width, height, depth) in voxels
        }
    
    def analyze_mask(self) -> Dict:
        """Perform analysis on current mask.
        
        Returns:
            Dictionary containing analysis results
        """
        if not self.data_manager or not self.data_manager.mask:
            return {}
            
        self._reset_measurements()
        mask_data = self.data_manager.mask_loader.nii_data
        
        # Get 3D mask by taking first channel/modality
        mask_3d = mask_data[..., 0]
        
        # Convert to binary mask if not already
        binary_mask = (mask_3d > 0).astype(np.uint8)
        
        # Calculate basic properties
        self.measurements['volume'] = np.sum(binary_mask)
        
        # Calculate surface area using marching cubes only if we have a valid mask
        if self.measurements['volume'] > 0:
            try:
                verts, faces, _, _ = measure.marching_cubes(binary_mask)
                self.measurements['surface_area'] = measure.mesh_surface_area(verts, faces)
            except Exception as e:
                print(f"Warning: Could not calculate surface area: {e}")
                self.measurements['surface_area'] = 0
        
            # Calculate centroid
            self.measurements['centroid'] = ndimage.center_of_mass(binary_mask)
            
            # Calculate bounding box
            coords = np.where(binary_mask > 0)
            min_coords = np.min(coords, axis=1)
            max_coords = np.max(coords, axis=1)
            self.measurements['bbox'] = (*min_coords, *max_coords)
            
            # Calculate dimensions
            dimensions = max_coords - min_coords + 1
            self.measurements['dimensions'] = tuple(dimensions)
        
        return self.measurements
    
    def get_formatted_results(self) -> Dict[str, str]:
        """Get analysis results formatted for display.
        
        Returns:
            Dictionary with formatted measurement strings
        """
        results = {}
        
        if self.measurements['volume'] > 0:
            results['Volume'] = f"{self.measurements['volume']:.2f} voxels"
            
            if self.measurements['surface_area'] > 0:
                results['Surface Area'] = f"{self.measurements['surface_area']:.2f} square voxels"
            
            if self.measurements['centroid']:
                cx, cy, cz = self.measurements['centroid']
                results['Centroid'] = f"({cx:.1f}, {cy:.1f}, {cz:.1f})"
                
            if self.measurements['dimensions']:
                w, h, d = self.measurements['dimensions']
                results['Dimensions'] = f"{w}×{h}×{d} voxels"
                
        return results