from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QAction, QActionGroup

class GuiController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Connect menu actions
        self.view.exit_action.triggered.connect(self.view.close)
        self.view.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        self.view.load_action.triggered.connect(self.load_nifti_file)

        # Default to light mode
        self.view.apply_light_mode()

        # Connect panel double-click events
        self.view.panel1.mouseDoubleClickEvent = lambda event: self.toggle_panel("Panel1")
        self.view.panel2.mouseDoubleClickEvent = lambda event: self.toggle_panel("Panel2")
        self.view.panel3.mouseDoubleClickEvent = lambda event: self.toggle_panel("Panel3")
        self.view.panel4.mouseDoubleClickEvent = lambda event: self.toggle_panel("Panel4")

        self.view.panel1.wheelEvent = lambda event: self.scroll_slice("x", event.angleDelta().y())
        self.view.panel2.wheelEvent = lambda event: self.scroll_slice("y", event.angleDelta().y())
        self.view.panel4.wheelEvent = lambda event: self.scroll_slice("z", event.angleDelta().y())
        
        self.view.checkbox_lock_layers.stateChanged.connect(self.lock_layers)
        
        
        #TODO
        # Connect checkbox_selection_mod to appropriate function

    def lock_layers(self):
        self.lock_layers = self.view.checkbox_lock_layers.isChecked()


    def scroll_slice(self, dimension, delta_y):
        if self.model.nii_data is not None and self.view.checkbox_lock_layers.isChecked() == True and self.model.expanded_panel == None:
            #step = abs(delta_y // 120)
            step = 1
            if delta_y > 0:
                # Scroll up: move slices in all dimensions
                for dim in ["x", "y", "z"]:
                    self.model.current_slice[dim] = max(self.model.current_slice[dim] - step, 0)
            else:
                # Scroll down: move slices in all dimensions
                for dim in ["x", "y", "z"]:
                    self.model.current_slice[dim] = min(self.model.current_slice[dim] + step,
                                                        self.model.nii_data.shape[{"x": 0, "y": 1, "z": 2}[dimension]] - 1)
            # Update the view to show the new slice
            self.update_views(self.model.current_modality_channel)
        elif self.model.nii_data is not None and (self.view.checkbox_lock_layers.isChecked() == True and self.model.expanded_panel != None) or (self.model.nii_data is not None and self.view.checkbox_lock_layers.isChecked() == False):
            #step = abs(delta_y // 120)
            step = 1
            if delta_y > 0:
                # Scroll up: move to the previous slice
                self.model.current_slice[dimension] = max(self.model.current_slice[dimension] - step, 0)
            else:
                # Scroll down: move to the next slice
                self.model.current_slice[dimension] = min(self.model.current_slice[dimension] + step,
                                                        self.model.nii_data.shape[{"x": 0, "y": 1, "z": 2}[dimension]] - 1)
            # Update the view to show the new slice
            self.update_view(dimension, self.model.current_modality_channel)


    def update_view(self, dimension, channel=0):
        if dimension == "x":
            x_slice = self.model.get_slice("x", self.model.current_slice["x"], channel)
            if x_slice is not None:
                self.view.update_slice(self.view.panel1, x_slice, self.model.get_current_slice_index("x"))
        elif dimension == "y":
            y_slice = self.model.get_slice("y", self.model.current_slice["y"], channel)
            if y_slice is not None:
                self.view.update_slice(self.view.panel2, y_slice, self.model.get_current_slice_index("y"))
        elif dimension == "z":
            z_slice = self.model.get_slice("z", self.model.current_slice["z"], channel)
            if z_slice is not None:
                self.view.update_slice(self.view.panel4, z_slice, self.model.get_current_slice_index("z"))


    def toggle_dark_mode(self):
        self.model.toggle_dark_mode()
        if self.model.dark_mode:
            self.view.apply_dark_mode()
        else:
            self.view.apply_light_mode()

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



    def load_nifti_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self.view, "Open NIfTI File", "", "NIfTI Files (*.nii *.nii.gz)")
        if file_path:
            self.model.load_nifti_file(file_path)
            self.update_views(self.model.current_modality_channel)
            self.update_modality_menu()

    def update_views(self, channel=0):
        x_slice = self.model.get_slice("x", self.model.current_slice["x"], channel)  
        if x_slice is not None:
            self.view.update_slice(self.view.panel1, x_slice, self.model.get_current_slice_index("x"))

        y_slice = self.model.get_slice("y", self.model.current_slice["y"], channel)
        if y_slice is not None:
            self.view.update_slice(self.view.panel2, y_slice, self.model.get_current_slice_index("y"))

        z_slice = self.model.get_slice("z", self.model.current_slice["z"], channel)
        if z_slice is not None:
            self.view.update_slice(self.view.panel4, z_slice, self.model.get_current_slice_index("z"))
            
    def update_modality_menu(self):
            self.view.modality_menu.clear()
            self.view.modality_group = QActionGroup(self.view.modality_menu)
            self.view.modality_group.setExclusive(True)
            for i in range(self.model.nii_data.shape[3]):
                action = QAction(str(i + 1), self.view)
                action.setCheckable(True)
                if i == 0:
                    action.setChecked(True)
                action.triggered.connect(lambda checked, i=i: self.change_modality(i))
                self.view.modality_group.addAction(action)
                self.view.modality_menu.addAction(action)

    def change_modality(self, channel):
        self.model.current_modality_channel = channel
        self.update_views(channel)