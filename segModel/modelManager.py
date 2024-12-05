import torch
from sam2.build_sam import build_sam2_video_predictor

class ModelManager:
    """
    Manages PyTorch device configuration and model initialization.
    """
    
    def __init__(self, model_config, checkpoint_path):
        self.device = self._select_device()
        print(f"Using device: {self.device}")
        
        if self.device.type == "cuda":
            torch.autocast("cuda", dtype=torch.bfloat16).__enter__()
            if torch.cuda.get_device_properties(0).major >= 8:
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
        elif self.device.type == "mps":
            print("\nSupport for MPS devices is preliminary.")

        self.predictor = build_sam2_video_predictor(model_config, checkpoint_path, device=self.device)


    @staticmethod
    def _select_device():
        if torch.cuda.is_available():
            return torch.device("cuda")
        elif torch.backends.mps.is_available():
            return torch.device("cpu")
        else:
            return torch.device("cpu")

    def get_predictor(self):
        return self.predictor