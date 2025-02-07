from model.file_loader import FileLoader
from model.nifti import Nifti

class DataManager:
    """Manages data access and file handlers for the application."""
    
    def __init__(self):
        self.image_loader = None
        self.mask_loader = None
        self.image = None
        self.mask = None

        
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