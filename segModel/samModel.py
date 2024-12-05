import os
import numpy as np
import nibabel as nib
from PIL import Image
import torch

class SamModel:
    """
    Handles segmentation processing for a given model.
    """
    
    def __init__(self, predictor, output_folder, scan_name):
        self.predictor = predictor
        self.output_folder = output_folder
        self.scan_name = scan_name
        self.masks = {} 

    def process_dimension(self, dimension, current_slice, pixel_x, pixel_y, label, modality):
        """
        Processes a specific dimension of the scan, starting from a given slice and propagating through the video.
        """
        scans_dir = os.path.join(self.output_folder, self.scan_name, f"modality_{modality}", f"scans_{dimension}")
        
        # Load and sort frame files
        frame_names = [
            p for p in os.listdir(scans_dir)
            if os.path.splitext(p)[-1].lower() in [".jpg", ".jpeg"]
        ]
        frame_names.sort(key=lambda p: int(os.path.splitext(p)[0]))

        # Initialize predictor state
        inference_state = self.predictor.init_state(video_path=scans_dir)
        self.predictor.reset_state(inference_state)

        # Add starting points
        points = np.array([[pixel_x, pixel_y]], dtype=np.float32)
        labels = np.array([1 if label == "P" else 0], dtype=np.int32)
        
        # Set starting points on the current slice
        self.predictor.add_new_points_or_box(
            inference_state=inference_state,
            frame_idx=current_slice,
            obj_id=1,
            points=points,
            labels=labels,
        )

        print(f"Starting from frame {current_slice}...")

        # Propagate results to subsequent frames
        for frame_idx, out_obj_ids, out_mask_logits in self.predictor.propagate_in_video(inference_state):
            if frame_idx >= len(frame_names): 
                break

            # Save mask
            mask = (out_mask_logits[0] > 0.0).cpu().numpy()
            self._save_mask(mask, dimension, modality, frame_idx)

    def _save_mask(self, mask, dimension, modality, slice_index):
        """
        Saves the generated mask as both .npy and .jpeg files.
        """
        save_path = os.path.join(self.output_folder, self.scan_name, f"modality_{modality}", f"masks_{dimension}")
        os.makedirs(save_path, exist_ok=True)

        # Save mask as .npy file
        mask_file_npy = os.path.join(save_path, f"{slice_index:04d}.npy")
        np.save(mask_file_npy, mask)

        # Flatten mask and normalize to [0, 255]
        mask_2d = mask[0, :, :]
        mask_normalized = (mask_2d * 255).astype(np.uint8)

        # Save mask as .jpeg file
        mask_file_jpeg = os.path.join(save_path, f"{slice_index:04d}.jpeg")
        mask_img = Image.fromarray(mask_normalized)
        mask_img.save(mask_file_jpeg)

    def _store_mask_for_nifti(self, mask, dimension, modality, slice_index):
        """
        Stores the mask in a dictionary for later NIfTI export.
        """
        key = (dimension, modality)
        if key not in self.masks:
            self.masks[key] = []
        self.masks[key].append((slice_index, mask))

    def export_to_nifti(self):
        """
        Converts masks into a NIfTI file.
        """
        nifti_path = os.path.join(self.output_folder, self.scan_name, "nifti_outputs")
        os.makedirs(nifti_path, exist_ok=True)

        for (dimension, modality), mask_data in self.masks.items():
            mask_data.sort(key=lambda x: x[0])
            volume = np.stack([data[1] for data in mask_data], axis=0)

            # Create NIfTI image
            nifti_img = nib.Nifti1Image(volume.astype(np.uint8), affine=np.eye(4))
            nifti_filename = os.path.join(nifti_path, f"{dimension}_modality_{modality}.nii.gz")
            nib.save(nifti_img, nifti_filename)

            print(f"Saved NIfTI file: {nifti_filename}")
