from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QAction, QActionGroup
from gui.view import MAIN_SPLITTER_SIZES, LEFT_SPLITTER_SIZES, RIGHT_SPLITTER_SIZES

class GuiController:
    """
    Controller class to manage interactions between the GUI view and the file_handler.
    """
    def __init__(self, filehandler, view):
        """
        Initialize the GUI Controller.

        Args:
            filehandler: The data filehandler containing the application's state and data.
            view: The GUI view for displaying and interacting with the user.
        """
        self.file_handler = filehandler
        self.view = view
        self.is_layers_locked = False
        self.expanded_panel = None
        self.is_updating_slider = False

        # Connect menu actions
        self.view.exit_action.triggered.connect(self.view.close)
        self.view.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        self.view.load_action.triggered.connect(self.load_nifti_file)

        # Default to light mode
        self.view.apply_light_mode()

        # Connect panel mouse events
        self.view.panel1.mouseDoubleClickEvent = lambda event: self.toggle_panel("Panel1-x")
        self.view.panel2.mouseDoubleClickEvent = lambda event: self.toggle_panel("Panel2-y")
        self.view.panel3.mouseDoubleClickEvent = lambda event: self.toggle_panel("Panel3")
        self.view.panel4.mouseDoubleClickEvent = lambda event: self.toggle_panel("Panel4-z")

        self.view.panel1.wheelEvent = lambda event: self.scroll_slice("x", event.angleDelta().y())
        self.view.panel2.wheelEvent = lambda event: self.scroll_slice("y", event.angleDelta().y())
        self.view.panel4.wheelEvent = lambda event: self.scroll_slice("z", event.angleDelta().y())

        self.view.checkbox_lock_layers.stateChanged.connect(self.lock_layers)
 
        self.view.reset_layers_button.clicked.connect(self.reset_layers)

        self.view.x_slice_slider.valueChanged.connect(lambda value: self.on_slider_value_changed("x", value))
        self.view.y_slice_slider.valueChanged.connect(lambda value: self.on_slider_value_changed("y", value))
        self.view.z_slice_slider.valueChanged.connect(lambda value: self.on_slider_value_changed("z", value))

        self.view.x_slice_slider.setEnabled(False)
        self.view.y_slice_slider.setEnabled(False)
        self.view.z_slice_slider.setEnabled(False)
        
        #TODO
        # Connect checkbox_selection_mod to appropriate function

    def on_slider_value_changed(self, dimension, value):
        """
        Handles the slider value change event and updates the current slice.
        """
        if not self.is_updating_slider:
            self.is_updating_slider = True  # Prevent recursion

            self.file_handler.current_slice[dimension] = value
            self.update_view(dimension, self.file_handler.current_modality_channel)
            if dimension == "x":
                self.view.x_slice_label.setText(f"X: {value}")
            elif dimension == "y":
                self.view.y_slice_label.setText(f"Y: {value}")
            elif dimension == "z":
                self.view.z_slice_label.setText(f"Z: {value}")
            
            self.is_updating_slider = False  # Re-enable event handling

    def initialize_sliders(self):
        self.view.x_slice_slider.setMinimum(0)
        self.view.x_slice_slider.setMaximum(self.file_handler.nii_data.shape[0] - 1)
        self.view.x_slice_slider.setValue(self.file_handler.current_slice["x"])

        self.view.y_slice_slider.setMinimum(0)
        self.view.y_slice_slider.setMaximum(self.file_handler.nii_data.shape[1] - 1)
        self.view.y_slice_slider.setValue(self.file_handler.current_slice["y"])

        self.view.z_slice_slider.setMinimum(0)
        self.view.z_slice_slider.setMaximum(self.file_handler.nii_data.shape[2] - 1)
        self.view.z_slice_slider.setValue(self.file_handler.current_slice["z"])

        self.view.x_slice_slider.setEnabled(True)
        self.view.y_slice_slider.setEnabled(True)
        self.view.z_slice_slider.setEnabled(True)

    def lock_layers(self):
        """
        Toggle the layer lock state based on the checkbox status.
        """
        self.is_layers_locked = self.view.checkbox_lock_layers.isChecked()

    def reset_layers(self):
        """
        Reset the layers to the default state.
        """
        if self.file_handler.nii_data is not None and self.expanded_panel is None:
            self.file_handler.current_slice = {"x": self.file_handler.nii_data.shape[0] // 2, "y": self.file_handler.nii_data.shape[1] // 2, "z": self.file_handler.nii_data.shape[2] // 2}
            self.update_views(self.file_handler.current_modality_channel)
        elif self.file_handler.nii_data is not None and self.expanded_panel is not None:
            dimension = self.expanded_panel[-1]
            self.file_handler.current_slice[dimension] = self.file_handler.nii_data.shape[{"x": 0, "y": 1, "z": 2}[dimension]] // 2
            self.update_view(dimension, self.file_handler.current_modality_channel)
        if self.file_handler.nii_data is not None:
            self.initialize_sliders()

    def scroll_slice(self, dimension, delta_y):
        """
        Handle scrolling through slices in a specified dimension.
        Ignores the dimension and scrolls only the current expanded panel if the layers are locked.

        Args:
            dimension (str): The dimension to scroll ("x", "y", or "z").
            delta_y (int): The scroll delta value.
        """
        if self.is_updating_slider:  # Avoid triggering value change event
            return
        
        if self.file_handler.nii_data is not None and self.is_layers_locked == True and self.expanded_panel is None:
            step = 1
            if delta_y > 0:
                for dim in ["x", "y", "z"]:
                    self.file_handler.current_slice[dim] = max(self.file_handler.current_slice[dim] - step, 0)
            else:
                for dim in ["x", "y", "z"]:
                    self.file_handler.current_slice[dim] = min(self.file_handler.current_slice[dim] + step,
                                                        self.file_handler.nii_data.shape[{"x": 0, "y": 1, "z": 2}[dim]] - 1)
            # Update the view to show the new slice
            self.update_views(self.file_handler.current_modality_channel)
            self.is_updating_slider = True
            self.view.x_slice_slider.setValue(self.file_handler.current_slice["x"])
            self.view.y_slice_slider.setValue(self.file_handler.current_slice["y"])
            self.view.z_slice_slider.setValue(self.file_handler.current_slice["z"])
            self.view.x_slice_label.setText(f"X: {self.file_handler.current_slice['x']}")
            self.view.y_slice_label.setText(f"Y: {self.file_handler.current_slice['y']}")
            self.view.z_slice_label.setText(f"Z: {self.file_handler.current_slice['z']}")
            self.is_updating_slider = False
        elif self.file_handler.nii_data is not None:
            step = 1
            if delta_y > 0:
                # Scroll up: move to the previous slice
                self.file_handler.current_slice[dimension] = max(self.file_handler.current_slice[dimension] - step, 0)
            else:
                # Scroll down: move to the next slice
                self.file_handler.current_slice[dimension] = min(self.file_handler.current_slice[dimension] + step,
                                                        self.file_handler.nii_data.shape[{"x": 0, "y": 1, "z": 2}[dimension]] - 1)
            # Update the view to show the new slice
            self.update_view(dimension, self.file_handler.current_modality_channel)
            self.is_updating_slider = True
            if dimension == "x":
                self.view.x_slice_slider.setValue(self.file_handler.current_slice["x"])
                self.view.x_slice_label.setText(f"X: {self.file_handler.current_slice['x']}")
            elif dimension == "y":
                self.view.y_slice_slider.setValue(self.file_handler.current_slice["y"])
                self.view.y_slice_label.setText(f"Y: {self.file_handler.current_slice['y']}")
            elif dimension == "z":
                self.view.z_slice_slider.setValue(self.file_handler.current_slice["z"])
                self.view.z_slice_label.setText(f"Z: {self.file_handler.current_slice['z']}")
            self.is_updating_slider = False

    def toggle_dark_mode(self):
        """
        Toggle between dark mode and light mode in the view.
        """
        if self.view.dark_mode_action.isChecked():
            self.view.apply_dark_mode()
        else:
            self.view.apply_light_mode()

    def toggle_panel(self, panel_name):
        """
        Toggle the expansion state of a specific panel.

        Args:
            panel_name (str): The name of the panel to toggle.
        """
        if self.file_handler.nii_data is None:
            return
        
        if self.expanded_panel == panel_name:
            # Reset to default layout
            self.view.main_splitter.setSizes(MAIN_SPLITTER_SIZES)
            self.view.left_splitter.setSizes(LEFT_SPLITTER_SIZES)
            self.view.right_splitter.setSizes(RIGHT_SPLITTER_SIZES)
            self.reset_expanded_panel()
            self.update_views(self.file_handler.current_modality_channel)
            self.view.x_slice_slider.setEnabled(True)
            self.view.y_slice_slider.setEnabled(True)
            self.view.z_slice_slider.setEnabled(True)
        else:
            # Expand the selected panel
            if panel_name == "Panel1-x":
                self.view.main_splitter.setSizes([800, 0, 200])
                self.view.left_splitter.setSizes([600, 0])
                if self.file_handler.nii_data is not None:
                    self.view.x_slice_slider.setEnabled(True)
                    self.view.y_slice_slider.setEnabled(False)
                    self.view.z_slice_slider.setEnabled(False)
            elif panel_name == "Panel4-z":
                self.view.main_splitter.setSizes([800, 0, 200])
                self.view.left_splitter.setSizes([0, 600])
                if self.file_handler.nii_data is not None:
                    self.view.x_slice_slider.setEnabled(False)
                    self.view.y_slice_slider.setEnabled(False)
                    self.view.z_slice_slider.setEnabled(True)
            elif panel_name == "Panel2-y":
                self.view.main_splitter.setSizes([0, 800, 200])
                self.view.right_splitter.setSizes([600, 0])
                if self.file_handler.nii_data is not None:
                    self.view.x_slice_slider.setEnabled(False)
                    self.view.y_slice_slider.setEnabled(True)
                    self.view.z_slice_slider.setEnabled(False)
            elif panel_name == "Panel3":
                self.view.main_splitter.setSizes([0, 800, 200])
                self.view.right_splitter.setSizes([0, 600])
                if self.file_handler.nii_data is not None:
                    self.view.x_slice_slider.setEnabled(False)
                    self.view.y_slice_slider.setEnabled(False)
                    self.view.z_slice_slider.setEnabled(False)
            self.set_expanded_panel(panel_name)

    def load_nifti_file(self):
        """
        Open a file dialog to load a NIfTI file and update the view.

        Raises:
            Exception: If an error occurs while loading the NIfTI file.
        """
        file_path, _ = QFileDialog.getOpenFileName(self.view, "Open NIfTI File", "", "NIfTI Files (*.nii *.nii.gz)")
        if file_path:
            try:
                self.file_handler.load_nifti_file(file_path)
                self.update_views(self.file_handler.current_modality_channel)
                self.update_modality_menu()
                self.initialize_sliders()
            except Exception as e:
                self.view.display_error(f"Failed to load NIfTI file: {str(e)}")

    def update_views(self, channel=0):
        """
        Update all slice views for a given modality channel.

        Args:
            channel (int): The modality channel index.
        """
        x_slice = self.file_handler.get_slice("x", self.file_handler.current_slice["x"], channel)  
        if x_slice is not None:
            self.view.update_slice(self.view.panel1, x_slice, self.file_handler.get_current_slice_index("x"))

        y_slice = self.file_handler.get_slice("y", self.file_handler.current_slice["y"], channel)
        if y_slice is not None:
            self.view.update_slice(self.view.panel2, y_slice, self.file_handler.get_current_slice_index("y"))

        z_slice = self.file_handler.get_slice("z", self.file_handler.current_slice["z"], channel)
        if z_slice is not None:
            self.view.update_slice(self.view.panel4, z_slice, self.file_handler.get_current_slice_index("z"))
            
    def update_view(self, dimension, channel=0):
        """
        Update the view for a specific dimension and channel.

        Args:
            dimension (str): The dimension to update ("x", "y", or "z").
            channel (int): The modality channel index.
        """
        if dimension == "x":
            x_slice = self.file_handler.get_slice("x", self.file_handler.current_slice["x"], channel)
            if x_slice is not None:
                self.view.update_slice(self.view.panel1, x_slice, self.file_handler.get_current_slice_index("x"))
        elif dimension == "y":
            y_slice = self.file_handler.get_slice("y", self.file_handler.current_slice["y"], channel)
            if y_slice is not None:
                self.view.update_slice(self.view.panel2, y_slice, self.file_handler.get_current_slice_index("y"))
        elif dimension == "z":
            z_slice = self.file_handler.get_slice("z", self.file_handler.current_slice["z"], channel)
            if z_slice is not None:
                self.view.update_slice(self.view.panel4, z_slice, self.file_handler.get_current_slice_index("z"))

    def update_modality_menu(self):
        """
        Update the modality menu with available channels from the NIfTI data.
        """
        self.view.modality_menu.clear()
        self.view.modality_group = QActionGroup(self.view.modality_menu)
        self.view.modality_group.setExclusive(True)
        for i in range(self.file_handler.nii_data.shape[3]):
            action = QAction(str(i + 1), self.view)
            action.setCheckable(True)
            if i == 0:
                action.setChecked(True)
            action.triggered.connect(lambda checked, i=i: self.change_modality(i))
            self.view.modality_group.addAction(action)
            self.view.modality_menu.addAction(action)

    def change_modality(self, channel):
        """
        Change the current modality channel and update the view.

        Args:
            channel (int): The modality channel index.
        """
        self.file_handler.current_modality_channel = channel
        if self.expanded_panel != None: 
            dimension = self.expanded_panel[-1]
            self.update_view(dimension, channel)
        else:
            self.update_views(channel)

    def set_expanded_panel(self, panel_name):
        """
        Set the expanded panel to a specific panel name.

        Args:
            panel_name (str): The name of the panel to expand.
        """
        self.expanded_panel = panel_name

    def reset_expanded_panel(self):
        """
        Reset the expanded panel to None.
        """
        self.expanded_panel = None
        