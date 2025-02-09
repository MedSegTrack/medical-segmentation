from typing import List, Tuple, Dict, Optional
import numpy as np
from .segmentationModel_interface import SegmentationModelInterface
from .sam2_model import Sam2Model
from config import CONFIG

PointType = Tuple[int, int]
LabelType = str
PointInfoType = List[Tuple[PointType, LabelType]]
PointsBySliceType = Dict[int, List[Tuple[int, int, str]]]

class SegmentationController:
    """Controls the segmentation process and manages communication between GUI and model.
    
    This class serves as an intermediary between the GUI and the segmentation model,
    handling initialization, running segmentation, and managing results.
    
    Attributes:
        data_manager: Manager for image and mask data
        model (Optional[SegmentationModelInterface]): Segmentation model instance
        config (Dict): Global configuration settings
        model_config (str): Model-specific configuration path
        checkpoint_path (str): Path to model checkpoint
        current_masks (Dict[str, np.ndarray]): Currently active segmentation masks
        is_initialized (bool): Whether model is properly initialized
    """
    
    def __init__(self, data_manager) -> None:
        """Initialize controller with data manager.
        
        Args:
            data_manager: Manager instance for handling image and mask data
        """
        self.data_manager = data_manager
        self.model: Optional[SegmentationModelInterface] = None
        self.config = CONFIG
        self.model_config = self.config['configuration_file']
        self.checkpoint_path = self.config['checkpoint_path']
        self.current_masks: Dict[str, np.ndarray] = {}
        self.is_initialized = False

    def initialize_model(self, 
                        checkpoint_path: Optional[str] = None, 
                        model_config: Optional[str] = None) -> bool:
        """Initialize the segmentation model.
        
        Args:
            checkpoint_path: Optional path to model weights
            model_config: Optional path to model configuration
            
        Returns:
            bool: True if initialization successful, False otherwise
            
        Raises:
            ValueError: If checkpoint_path is not a string
        """
        if checkpoint_path is None:
            checkpoint_path = self.checkpoint_path
        if model_config is None:
            model_config = self.model_config

        try:
            if not isinstance(checkpoint_path, str):
                raise ValueError(f"Checkpoint path must be string, got {type(checkpoint_path)}")

            self.model = Sam2Model(model_config)
            self.is_initialized = self.model.initialize(checkpoint_path)
            return self.is_initialized
        except Exception as e:
            print(f"Failed to initialize model: {e}")
            return False

    def run_segmentation(self, 
                        points_by_slice: PointsBySliceType,
                        dimension: str) -> Dict[str, np.ndarray]:
        """Run segmentation process on specified axis with given points.
        
        Args:
            points_by_slice: Dictionary mapping slice indices to lists of point information
                Each point info is (x, y, label) where label is "P" for positive
            dimension: Current dimension for result storage
                
        Returns:
            Dict mapping "dimension_index" to mask arrays
            
        Raises:
            RuntimeError: If model not initialized
        """
        if not self.is_initialized or self.model is None:
            raise RuntimeError("Model not initialized")

        try:
            scans_directory = self.data_manager.prepare_for_segmentation(dimension)
            self.model.set_state(scans_directory)

            # Process points for each slice
            for slice_idx, points_info in points_by_slice.items():
                points = np.array([[x, y] for x, y, _ in points_info], dtype=np.float32)
                labels = np.array([1 if label == "P" else 0 for _, _, label in points_info], 
                                dtype=np.int32)

                print(f"Adding prompt from slice: {dimension}:{slice_idx}")
                print(f"Points: {points}")
                print(f"Labels: {labels}")

                self.model.add_prompt(slice_idx, points, labels)
                
            # Run bi-directional propagation
            forward_masks = self.model.propagate("forward")
            backward_masks = self.model.propagate("backward")
            
            # Merge and store results
            for idx, mask in {**forward_masks, **backward_masks}.items():
                self.current_masks[f"{dimension}_{idx}"] = mask
                    
            return self.current_masks
                
        except Exception as e:
            print(f"Segmentation failed: {e}")
            return {}

    def get_mask(self, dimension: str, slice_index: int) -> Optional[np.ndarray]:
        """Retrieve mask for specific dimension and slice.
        
        Args:
            dimension: Dimension identifier ("x", "y", or "z")
            slice_index: Index of the slice
            
        Returns:
            Mask array if available, None otherwise
        """
        return self.current_masks.get(f"{dimension}_{slice_index}")

    def clear_masks(self) -> None:
        """Clear all stored segmentation masks."""
        self.current_masks.clear()

    def save_state(self) -> Dict:
        """Save current model state for later restoration.
        
        Returns:
            Dictionary containing model state information
        """
        if self.model:
            return self.model.get_state()
        return {}

    def load_state(self, state: Dict) -> None:
        """Restore model to previously saved state.
        
        Args:
            state: Previously saved model state
        """
        if self.model:
            self.model.set_state(state)