import torch
import numpy as np
from typing import List, Tuple, Dict, Any
from .segmentationModel_interface import SegmentationModelInterface
from sam2.build_sam import build_sam2_video_predictor
import os

class Sam2Model(SegmentationModelInterface):
    """SAM2 model implementation for video segmentation.
    
    This class implements the SegmentationModelInterface for the SAM2 model,
    providing functionality for:
    - Model initialization and device management
    - Adding segmentation prompts
    - Propagating segmentation through video frames
    - Managing model state
    
    Attributes:
        model_config (Dict): Configuration for the SAM2 model
        device (torch.device): Computing device (CPU/CUDA/MPS)
        predictor: SAM2 video predictor instance
        inference_state: Current state of the segmentation
    """
    
    def __init__(self, model_config: Dict) -> None:
        """Initialize SAM2 model with configuration.
        
        Args:
            model_config (Dict): Model configuration parameters
        """
        self.model_config = model_config
        self.device = self._select_device()
        self.predictor = None
        self.inference_state = None
        print(f"Using device: {self.device}")

    def initialize(self, checkpoint_path: str = None) -> bool:
        """Initialize the model with checkpoint.
        
        Args:
            checkpoint_path: Path to model checkpoint (str) or config dict with path
            
        Returns:
            bool: True if initialization successful
        """
            
        try:
            if not isinstance(checkpoint_path, str):
                raise ValueError(f"Checkpoint path must be string, got {type(checkpoint_path)}")

            if not os.path.exists(checkpoint_path):
                raise FileNotFoundError(f"Checkpoint not found at: {checkpoint_path}")
            
            print(f"Loading model from: {checkpoint_path}")

            # Initialize predictor with device
            self.predictor = build_sam2_video_predictor(
                self.model_config,
                checkpoint_path,
                device=self._select_device()
            )

            print("Model initialized")

            return True

        except Exception as e:
            print(f"Model initialization failed: {str(e)}")
            return False

    def add_prompt(self, 
                  slice_index: int,
                  points: np.ndarray,
                  labels: np.ndarray) -> Tuple[None, List[int], torch.Tensor]:
        """Add segmentation prompt points for a specific slice.
        
        Args:
            slice_index (int): Index of the slice to add prompt to
            points (np.ndarray): Array of prompt points, shape (N, 2)
            labels (np.ndarray): Array of point labels (1 for positive, 0 for negative)
            
        Returns:
            Tuple containing:
            - None
            - List of object IDs
            - Tensor of mask logits
            
        Raises:
            RuntimeError: If model or inference state not initialized
        """
        if self.predictor is None:
            raise RuntimeError("Model not initialized")
        
        if self.inference_state is None:
            raise RuntimeError("inference_state not initialized")

        return self.predictor.add_new_points_or_box(
            inference_state=self.inference_state,
            frame_idx=slice_index,
            obj_id=1,
            points=points,
            labels=labels,
        )

    def propagate(self, direction: str = "forward", progress_callback=None) -> Dict[int, np.ndarray]:
        """Propagate segmentation from current state through video frames.
        
        Args:
            direction (str): Propagation direction ("forward" or "backward")
            progress_callback (callable): Callback for progress updates
            
        Returns:
            Dict[int, np.ndarray]: Mapping of frame indices to mask arrays
        """
        if self.predictor is None or self.inference_state is None:
            raise RuntimeError("Model not initialized or no inference state")

        masks: Dict[int, np.ndarray] = {}
        is_reverse = direction == "backward"
        
        # Get current frame and total frames
        total_frames = len(self.inference_state['images'])
        processed = 0
        
        for frame_idx, out_obj_ids, out_mask_logits in self.predictor.propagate_in_video(
            self.inference_state, 
            reverse=is_reverse 
        ):  
            processed += 1
            if progress_callback:
                progress = int((processed / total_frames) * 100)
                progress_callback(progress)
                
            for obj_id, mask_logits in zip(out_obj_ids, out_mask_logits):
                mask = (mask_logits > 0.0).cpu().numpy()
                masks[frame_idx] = mask

        return masks

    def get_state(self) -> Any:
        """Get current model inference state.
        
        Returns:
            Any: Current inference state object
            
        Raises:
            RuntimeError: If no inference state is available
        """
        if self.inference_state is None:
            raise RuntimeError("No inference state available")
        return self.inference_state

    def set_state(self, path: str) -> None:
        """Set model state with video path.
        
        Args:
            path (str): Path to video frames directory
        """
        self.inference_state = self.predictor.init_state(video_path=path)
        self.predictor.reset_state(self.inference_state)

    def _select_device(self) -> torch.device:
        """Select appropriate computing device with fallback handling.
        
        Returns:
            torch.device: Selected computing device (CUDA > MPS > CPU)
        """
        if torch.cuda.is_available():
            return torch.device("cuda")
        elif torch.backends.mps.is_available():
            return torch.device("cpu")
        return torch.device("cpu")