from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Union
import numpy as np
import torch

# Custom type definitions
PointType = Tuple[int, int]
PointsType = List[PointType]
LabelsType = List[str]
MaskType = Union[np.ndarray, torch.Tensor]
StateType = Dict[str, Any]

class SegmentationModelInterface(ABC):
    """Abstract base class defining interface for segmentation models.
    
    This interface defines the required methods that any segmentation model
    implementation must provide. It ensures consistent interaction between
    different model implementations and the rest of the application.
    
    Methods:
        initialize: Set up model with weights from checkpoint
        add_prompt: Add segmentation prompts for a specific slice
        propagate: Propagate segmentation through neighboring slices
        get_state: Retrieve current model state
        set_state: Restore model to a specific state
    """

    @abstractmethod
    def initialize(self, checkpoint_path: str) -> bool:
        """Initialize the model with given checkpoint.
        
        Args:
            checkpoint_path (str): Path to model weights checkpoint file
            
        Returns:
            bool: True if initialization successful, False otherwise
            
        Raises:
            FileNotFoundError: If checkpoint file doesn't exist
            RuntimeError: If model initialization fails
        """
        pass

    @abstractmethod
    def add_prompt(self, 
                  slice_index: int,
                  points: PointsType,
                  labels: LabelsType) -> MaskType:
        """Add segmentation prompt points for specific slice.
        
        Args:
            slice_index (int): Index of the target slice
            points (List[Tuple[int, int]]): List of (x, y) coordinates for prompt points
            labels (List[str]): Point labels ("P" for positive, "N" for negative)
            
        Returns:
            Union[np.ndarray, torch.Tensor]: Generated mask for the slice
            
        Raises:
            ValueError: If points and labels lengths don't match
            RuntimeError: If model not initialized
        """
        pass

    @abstractmethod
    def propagate(self, direction: str = "forward") -> Dict[int, MaskType]:
        """Propagate segmentation from current slice to neighboring slices.
        
        Args:
            direction (str): Propagation direction ("forward" or "backward")
            
        Returns:
            Dict[int, Union[np.ndarray, torch.Tensor]]: Mapping of slice indices to masks
            
        Raises:
            RuntimeError: If no prompt points added or model not initialized
            ValueError: If invalid direction specified
        """
        pass
        
    @abstractmethod
    def get_state(self) -> StateType:
        """Get current model state for serialization.
        
        Returns:
            Dict[str, Any]: Dictionary containing current model state
            
        Raises:
            RuntimeError: If model not initialized
        """
        pass

    @abstractmethod
    def set_state(self, state: StateType) -> None:
        """Restore model to specified state.
        
        Args:
            state (Dict[str, Any]): Previously saved model state
            
        Raises:
            ValueError: If invalid state format
            RuntimeError: If model not initialized
        """
        pass