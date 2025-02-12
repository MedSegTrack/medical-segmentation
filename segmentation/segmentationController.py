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
        self._is_cancelled = False

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
                        dimension: str,
                        modality: int) -> Dict[str, np.ndarray]:
        """Run segmentation process on specified axis with given points."""
        if not self.is_initialized or self.model is None:
            raise RuntimeError("Model not initialized")

        self._is_cancelled = False
        
        try:
            scans_directory = self.data_manager.prepare_for_segmentation(dimension, modality)
            self.model.set_state(scans_directory)

            # Process points for each slice without progress updates
            for slice_idx, points_info in points_by_slice.items():
                if self._is_cancelled:
                    return {}

                self.status_callback(f"Adding prompt for slice {slice_idx}...")

                points = np.array([[x, y] for x, y, _ in points_info], dtype=np.float32)
                labels = np.array([1 if label == "P" else 0 for _, _, label in points_info], 
                                dtype=np.int32)

                self.model.add_prompt(slice_idx, points, labels)
                
            # Run forward propagation (0-50%)
            if hasattr(self, 'status_callback'):
                self.status_callback("Running forward propagation...")
            forward_masks = self.model.propagate(
                "forward",
                progress_callback=lambda p: self.progress_callback(int(p))  # 0-50%
            )
            if self._is_cancelled:
                return {}
        

            # Run backward propagation (50-100%)
            if hasattr(self, 'status_callback'):
                self.status_callback("Running backward propagation...")
            backward_masks = self.model.propagate(
                "backward",
                progress_callback=lambda p: self.progress_callback(50 + int(p))  # 50-100%
            )
            if self._is_cancelled:
                return {}
            
            # Merge and store results
            for idx, mask in {**forward_masks, **backward_masks}.items():
                self.current_masks[f"{dimension}_{idx}"] = mask

            self.data_manager.create_mask_from_segmentation(self.current_masks, dimension)
                    
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

    def cancel_segmentation(self):
        """Cancel ongoing segmentation process."""
        self._is_cancelled = True