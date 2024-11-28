import nibabel as nib

class GuiModel:
    def __init__(self):
        self.expanded_panel = None
        self.dark_mode = False
        self.nii_data = None
        self.current_slice = {"x": 0, "y": 0, "z": 0}
        self.current_modality_channel = 0

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode

    def load_nifti_file(self, path):
        nifti_img = nib.load(path)
        self.nii_data = nifti_img.get_fdata()
        self.current_slice = {"x": self.nii_data.shape[0] // 2, "y": self.nii_data.shape[1] // 2, "z": self.nii_data.shape[2] // 2}

    def set_expanded_panel(self, panel_name):
        self.expanded_panel = panel_name

    def reset_expanded_panel(self):
        self.expanded_panel = None

    def get_slice(self, dimension, index, channel=0):
        if self.nii_data is None:
            return None
    
        if dimension == "x":
            if index < self.nii_data.shape[0]:
                return self.nii_data[index, :, :, channel]
        elif dimension == "y":
            if index < self.nii_data.shape[1]:
                return self.nii_data[:, index, :, channel]
        elif dimension == "z":
            if index < self.nii_data.shape[2]:
                return self.nii_data[:, :, index, channel]
    
        return None

        
    def toggle_panel(self, panel_name):
        if self.model.expanded_panel == panel_name:
            # Reset to default layout
            self.view.main_splitter.setSizes([400, 400, 200])
            self.view.left_splitter.setSizes([300, 300])
            self.view.right_splitter.setSizes([300, 300])
            self.model.reset_expanded_panel()
        else:
            # Expand the selected panel while keeping Side Options Panel visible
            if panel_name == "Panel1":
                self.view.main_splitter.setSizes([800, 0, 200])
                self.view.left_splitter.setSizes([600, 0])
            elif panel_name == "Panel4":
                self.view.main_splitter.setSizes([800, 0, 200])
                self.view.left_splitter.setSizes([0, 600])
            elif panel_name == "Panel2":
                self.view.main_splitter.setSizes([0, 800, 200])
                self.view.right_splitter.setSizes([600, 0])
            elif panel_name == "Panel3":
                self.view.main_splitter.setSizes([0, 800, 200])
                self.view.right_splitter.setSizes([0, 600])
            self.model.set_expanded_panel(panel_name)

    def get_current_slice_index(self, dimension):
        return self.current_slice.get(dimension, 1)


