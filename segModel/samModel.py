import os
import numpy as np
import nibabel as nib
from PIL import Image, ImageDraw

class SamModel:
    """
    Handles segmentation processing for a given model.
    """
    
    def __init__(self, predictor, output_folder, scan_name):
        self.predictor = predictor
        self.output_folder = output_folder
        self.scan_name = scan_name
        self.masks = {} 

    def process_dimension(self, dimension, current_slice, points_info, modality):
        """
        Processes a specific dimension of the scan, starting from a given slice and propagating multiple points.
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
        points = np.array([[x, y] for x, y, _ in points_info], dtype=np.float32)
        labels = np.array([1 if label == "P" else 0 for _, _, label in points_info], dtype=np.int32)

        start_index = frame_names.index(str(current_slice)+'.jpeg')

        # Set starting points on the current slice
        self.predictor.add_new_points_or_box(
            inference_state=inference_state,
            frame_idx=start_index,
            obj_id=1,
            points=points,
            labels=labels,
        )

        print(f"Starting from frame {current_slice}...")

        # Propagate forward results to subsequent frames
        for frame_idx, out_obj_ids, out_mask_logits in self.predictor.propagate_in_video(inference_state):
            if frame_idx >= len(frame_names): 
                break

            for obj_id, mask_logits in zip(out_obj_ids, out_mask_logits):

                mask = (mask_logits > 0.0).cpu().numpy()

                # Save mask
                frame_path = os.path.join(scans_dir, frame_names[frame_idx])
                self._save_mask(mask, dimension, modality, frame_idx, os.path.join(scans_dir, frame_names[frame_idx]), points_info, obj_id=obj_id)
        
        # Propagate backward results to subsequent frames
        for frame_idx, out_obj_ids, out_mask_logits in self.predictor.propagate_in_video(inference_state, reverse=True):
            if frame_idx >= len(frame_names): 
                break

            for obj_id, mask_logits in zip(out_obj_ids, out_mask_logits):

                mask = (mask_logits > 0.0).cpu().numpy()

                # Save mask
                frame_path = os.path.join(scans_dir, frame_names[frame_idx])
                self._save_mask(mask, dimension, modality, frame_idx, os.path.join(scans_dir, frame_names[frame_idx]), points_info, obj_id=obj_id)


    def _save_mask(self, mask, dimension, modality, slice_index, frame_path, points_info, obj_id=None):
        """
        Saves the generated mask as both .npy and .jpeg files, optionally distinguishing objects by obj_id.
        Also saves the mask overlaid on the original frame with partial transparency, and draws points with labels.
        """
        save_path = os.path.join(self.output_folder, self.scan_name, f"modality_{modality}", f"masks_{dimension}")
        os.makedirs(save_path, exist_ok=True)

        file_suffix = f"_{obj_id}" if obj_id is not None else ""
        
        # Save mask as .npy file
        mask_file_npy = os.path.join(save_path, f"{slice_index:04d}{file_suffix}.npy")
        np.save(mask_file_npy, mask)

        # Flatten mask and normalize to [0, 255]
        mask_2d = mask[0, :, :] if len(mask.shape) == 3 else mask  # Obsługuje zarówno 2D, jak i 3D maski.
        mask_normalized = (mask_2d * 255).astype(np.uint8)

        # Save mask as .jpeg file
        mask_file_jpeg = os.path.join(save_path, f"{slice_index:04d}{file_suffix}.jpeg")
        mask_img = Image.fromarray(mask_normalized)
        mask_img.save(mask_file_jpeg)

        # Overlay mask on original image with partial transparency
        original_image = Image.open(frame_path).convert("RGBA")  # Convert original image to RGBA
        mask_overlay = Image.fromarray(mask_normalized).convert("L")  # Mask to grayscale

        # Create a red semi-transparent overlay only for the masked areas
        red_overlay = Image.new("RGBA", original_image.size, (0, 0, 0, 0))  # Start with a fully transparent image

        # Paste red color into the overlay where the mask is active
        red_overlay.paste((255, 0, 0, 128), (0, 0), mask_overlay)  # Red color with 50% opacity (128/255)

        # Make sure the alpha value is 50% to add transparency
        red_overlay_with_alpha = red_overlay.copy()
        red_overlay_with_alpha.putalpha(128)  # Set alpha to 50% transparency (128 out of 255)

        # Composite the original image with the red overlay, ensuring the overlay is on top
        combined = Image.alpha_composite(original_image, red_overlay_with_alpha)

        # Draw points on the overlay
        draw = ImageDraw.Draw(combined)

        # Draw points
        for x, y, label in points_info:
            point_color = (0, 255, 0) if label == 'P' else (255, 0, 0)
            radius = 5

            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=point_color)

        # Save the final image with the points and overlay
        overlay_file_jpeg = os.path.join(save_path, f"{slice_index:04d}{file_suffix}_overlay_with_points.jpeg")
        combined.convert("RGB").save(overlay_file_jpeg)

        self._store_mask_for_nifti(mask, dimension, modality, slice_index)

    def _store_mask_for_nifti(self, mask, dimension, modality, slice_index):
        """
        Stores the mask in a dictionary for later NIfTI export.
        """
        if mask.dtype != np.uint8:
            mask = mask.astype(np.uint8)
        
        key = (dimension, modality)
        
        if key not in self.masks:
            self.masks[key] = []
        
        self.masks[key].append((slice_index, mask))

    def export_to_nifti(self):
        """
        Exports masks to a NIfTI file with fixed shape (240, 240, 155).
        """
        nifti_path = os.path.join(self.output_folder, self.scan_name, "nifti_outputs")
        os.makedirs(nifti_path, exist_ok=True)

        for (dimension, modality), mask_data in self.masks.items():
            # Sort mask data by slice index
            mask_data.sort(key=lambda x: x[0])  # Sort by slice index

            # Prepare an empty volume of the target shape
            target_shape = (240, 240, 155)
            volume = np.zeros(target_shape, dtype=np.uint8)

            # Fill the volume with the available masks
            for slice_index, mask in mask_data:
                if 0 <= slice_index < target_shape[2]:
                    volume[:, :, slice_index] = mask

            # Create NIfTI image
            nifti_img = nib.Nifti1Image(volume, affine=np.eye(4))

            # Save NIfTI file
            nifti_filename = os.path.join(nifti_path, f"{dimension}_modality_{modality}.nii.gz")
            nib.save(nifti_img, nifti_filename)
            print(f"Saved NIfTI file: {nifti_filename}")
