from PyQt5.QtWidgets import QAction, QActionGroup, QListWidgetItem
from PyQt5.QtCore import Qt
from gui.view import MAIN_SPLITTER_SIZES, LEFT_SPLITTER_SIZES, RIGHT_SPLITTER_SIZES
from gui.filepopup import LoadFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from segModel.dataManager import DataManager
from segModel.samModel import SamModel
from segModel.modelManager import ModelManager
import os
from tqdm import tqdm
from collections import defaultdict

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
        self.data_manager = DataManager()

        sam2_checkpoint = "checkpoints/sam2.1_hiera_large.pt"
        model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"

        self.model_manager = ModelManager(model_cfg, sam2_checkpoint)

        self.segmentation_output_dir = "output"

        self.view = view
        self.is_layers_locked = False
        self.expanded_panel = None
        self.is_updating_slider = False
        self.selection_list = []
        self.is_selection_mode = False

        self._initialize_actions()
        self._connect_panel_events()
        self._initialize_sliders()

    def _initialize_sliders(self):
        """Set initial state for slice sliders."""
        for slider in [self.view.x_slice_slider, self.view.y_slice_slider, self.view.z_slice_slider]:
            slider.setEnabled(False)

    def _initialize_actions(self):
        """Initialize and connect menu actions."""
        self.view.exit_action.triggered.connect(self.view.close)
        self.view.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        self.view.load_action.triggered.connect(self.load_nifti_file)
        self.view.apply_light_mode()

        self.view.checkbox_lock_layers.stateChanged.connect(self.lock_layers)
        self.view.reset_layers_button.clicked.connect(self.reset_layers)

        self.view.x_slice_slider.valueChanged.connect(lambda value: self.on_slider_value_changed("x", value))
        self.view.y_slice_slider.valueChanged.connect(lambda value: self.on_slider_value_changed("y", value))
        self.view.z_slice_slider.valueChanged.connect(lambda value: self.on_slider_value_changed("z", value))

        self.view.reset_selection_button.clicked.connect(self.clear_selection_list)
        self.view.checkbox_selection_mode.stateChanged.connect(self.toggle_selection_mode)

        self.view.run_segmentation_button.clicked.connect(self.start_segmentation)

    def _connect_panel_events(self):
        """Connect panel-specific mouse and wheel events."""
        for dimension, panel in zip(["x", "y", "z", "3d"], [self.view.panel1, self.view.panel2, self.view.panel4]):
            panel.mouseDoubleClickEvent = lambda event, dim=dimension: self.toggle_panel(f"Panel-{dim}")
            panel.wheelEvent = lambda event, dim=dimension: self.scroll_slice(dim, event.angleDelta().y())
            panel.mousePressEvent = lambda event, dim=dimension: self.mouse_click_selection(event, dim)

    def update_sliders(self):
        dimension = ['x', 'y', 'z']
        for dim in dimension:
            slider = getattr(self.view, f"{dim}_slice_slider")
            slider.setMinimum(0)
            slider.setMaximum(self.file_handler.nii_data.shape[dimension.index(dim)] - 1)
            slider.setValue(self.file_handler.current_slice[dim])
            if self.expanded_panel is None:
                slider.setEnabled(True)
            else:
                slider.setEnabled(False)
        if self.expanded_panel is not None:
            cur_slider = getattr(self.view, f"{self.expanded_panel[-1]}_slice_slider")
            cur_slider.setEnabled(True)

    def clear_selection_list(self):
        """
        Clear the selection list.
        """
        self.selection_list = []
        self.update_panels(self.file_handler.current_modality_channel)
        self.update_list_view()

    def toggle_selection_mode(self):
        """
        Toggle the selection mode.
        """
        self.is_selection_mode = self.view.checkbox_selection_mode.isChecked()

    def mouse_click_selection(self, event, dimension):
        """
        Handle mouse click selection event in a slice view panel.

        Args:
            event: The mouse event.
            dimension (str): The dimension of the slice view panel ("x", "y", or "z").
        """
        if self.file_handler.nii_data is None or not self.is_selection_mode:
            return

        # Map dimension to the correct panel
        panels = {"x": self.view.panel1, "y": self.view.panel2, "z": self.view.panel4} 
        panel = panels.get(dimension) 
        if panel is None: 
            return

        canvas = panel.figure.gca()
        image_extent = canvas.get_images()[0].get_extent()  # Get image extent (left, right, bottom, top)
        left, right, top, bottom = image_extent
        # Get mouse click position in canvas coordinates
        dpr = panel.devicePixelRatio()
        click_x = event.pos().x() * dpr
        click_y = event.pos().y() * dpr
        
        # Transform canvas coordinates into image coordinates
        inv = canvas.transData.inverted()
        image_coords = inv.transform((click_x, click_y))
        image_x, image_y = image_coords

        # Check if the click is within the image bounds
        if left <= image_x <= right and bottom <= image_y <= top:
            # Convert to pixel coordinates of the image
            img_width = right - left
            img_height = top - bottom
            current_slice = self.file_handler.current_slice[dimension]
            
            dimension_map = {
                "x": self.file_handler.nii_data[0],
                "y": self.file_handler.nii_data[1],
                "z": self.file_handler.nii_data
            }
            
            nii_data = dimension_map[dimension]
            # Determine shape based on whether it's "z" or others
            if dimension in ["x", "y"]:
                shape_x, shape_y = nii_data.shape[1], nii_data.shape[0]
            else:  # For "z"
                shape_x, shape_y = nii_data.shape[1], nii_data.shape[0]
            # Calculate pixel values
            pixel_x = int((image_x - left) / img_width * shape_x)
            pixel_y = int((image_y - bottom) / img_height * shape_y)

            if event.button() == Qt.LeftButton:
                self.selection_list.append((dimension, current_slice, pixel_x, pixel_y, "P"))
            elif event.button() == Qt.RightButton:
                self.selection_list.append((dimension, current_slice, pixel_x, pixel_y, "N"))

            self.update_panels(self.file_handler.current_modality_channel)
            self.update_list_view()

    def toggle_show_mask(self, mask_index):
        """
        Toggle the mask visibility in the view.
        
        Args:
            mask_index (int): The index of the mask to toggle. 0 toggles all masks
        """
        def toggle_all_masks(state):
            self.file_handler.show_mask = [state] * self.file_handler.nii_mask_channels
        
        if mask_index == 0:
            # Toggle all masks
            new_state = not all(self.file_handler.show_mask)
            toggle_all_masks(new_state)
        else:
            self.file_handler.show_mask[mask_index] = not self.file_handler.show_mask[mask_index]
            self.file_handler.show_mask[0] = False

        self.update_mask_menu()
        self.update_panels(self.file_handler.current_modality_channel)

    def on_slider_value_changed(self, dimension, value):
        """
        Handles the slider value change event and updates the current slice.
        """
        if not self.is_updating_slider:
            self.is_updating_slider = True  # Prevent recursion

            self.file_handler.current_slice[dimension] = value
            self.update_panels(self.file_handler.current_modality_channel)
            if dimension == "x":
                self.view.x_slice_label.setText(f"X: {value}")
            elif dimension == "y":
                self.view.y_slice_label.setText(f"Y: {value}")
            elif dimension == "z":
                self.view.z_slice_label.setText(f"Z: {value}")
            
            self.is_updating_slider = False  # Re-enable event handling

    def lock_layers(self):
        """
        Toggle the layer lock state based on the checkbox status.
        """
        self.is_layers_locked = self.view.checkbox_lock_layers.isChecked()

    def reset_layers(self):
        """
        Reset the layers to the default state.
        """
        if self.file_handler.nii_data is not None:
            self.file_handler.current_slice = {"x": self.file_handler.nii_data.shape[0] // 2, "y": self.file_handler.nii_data.shape[1] // 2, "z": self.file_handler.nii_data.shape[2] // 2}
            self.update_panels(self.file_handler.current_modality_channel)
            self.update_sliders()

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

        def update_current_slices(dimensions):
            for dim in dimensions:
                if delta_y > 0:
                    self.file_handler.current_slice[dim] = max(self.file_handler.current_slice[dim] - 1, 0)
                else:
                    self.file_handler.current_slice[dim] = min(self.file_handler.current_slice[dim] + 1,
                                                            self.file_handler.nii_data.shape[{"x": 0, "y": 1, "z": 2}[dim]] - 1)
                getattr(self.view, f"{dim}_slice_slider").setValue(self.file_handler.current_slice[dim])
                getattr(self.view, f"{dim}_slice_label").setText(f"{dim.upper()}: {self.file_handler.current_slice[dim]}")

        if self.file_handler.nii_data is not None:
            self.is_updating_slider = True
            if self.is_layers_locked and self.expanded_panel is None:
                update_current_slices(["x", "y", "z"])
            else:
                update_current_slices([dimension])
            self.update_panels(self.file_handler.current_modality_channel)
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
            self.update_panels(self.file_handler.current_modality_channel)
            self.view.x_slice_slider.setEnabled(True)
            self.view.y_slice_slider.setEnabled(True)
            self.view.z_slice_slider.setEnabled(True)
        else:
            # Expand the selected panel
            if panel_name == "Panel-x":
                self.view.main_splitter.setSizes([800, 0, 200])
                self.view.left_splitter.setSizes([600, 0])
                if self.file_handler.nii_data is not None:
                    self.view.x_slice_slider.setEnabled(True)
                    self.view.y_slice_slider.setEnabled(False)
                    self.view.z_slice_slider.setEnabled(False)
            elif panel_name == "Panel-z":
                self.view.main_splitter.setSizes([800, 0, 200])
                self.view.left_splitter.setSizes([0, 600])
                if self.file_handler.nii_data is not None:
                    self.view.x_slice_slider.setEnabled(False)
                    self.view.y_slice_slider.setEnabled(False)
                    self.view.z_slice_slider.setEnabled(True)
            elif panel_name == "Panel-y":
                self.view.main_splitter.setSizes([0, 800, 200])
                self.view.right_splitter.setSizes([600, 0])
                if self.file_handler.nii_data is not None:
                    self.view.x_slice_slider.setEnabled(False)
                    self.view.y_slice_slider.setEnabled(True)
                    self.view.z_slice_slider.setEnabled(False)
            elif panel_name == "Panel-3d":
                self.view.main_splitter.setSizes([0, 800, 200])
                self.view.right_splitter.setSizes([0, 600])
                if self.file_handler.nii_data is not None:
                    self.view.x_slice_slider.setEnabled(False)
                    self.view.y_slice_slider.setEnabled(False)
                    self.view.z_slice_slider.setEnabled(False)
            self.set_expanded_panel(panel_name)

    def load_nifti_file(self):
        """
        Open a dialog to load a NIfTI file and optionally a NIfTI mask file.
        Update the view with the loaded data.

        Raises:
            Exception: If an error occurs while loading the NIfTI file or mask.
        """
        # Create the dialog for loading files
        dialog = LoadFileDialog(self.view.dark_mode_action.isChecked())
        if dialog.exec_():
            try:
                self.file_handler.nii_data = None
                self.file_handler.nii_mask = None
                # Load the primary NIfTI file
                if hasattr(dialog, 'nifti_path'):
                    self.file_handler.load_nifti_file(dialog.nifti_path)
                    self.update_modality_menu()
                    self.update_sliders()
                # Load the optional mask file if the checkbox is checked
                if dialog.checkbox.isChecked() and hasattr(dialog, 'mask_path'):
                    self.file_handler.load_nifti_mask(dialog.mask_path)
                    self.update_mask_menu()
                    
                self.update_panels(self.file_handler.current_modality_channel)
                
            except Exception as e:
                self.view.display_error(f"Failed to load files: {str(e)}")

    def update_panels(self, channel=0, dimensions=["x", "y", "z"]):
        """
        Update all slice views for given dimensions and modality channel.

        Args:
            dimensions (list): List of dimensions to update.
            channel (int): The modality channel index.
        """
        if self.expanded_panel is not None:
            self.update_panel(self.expanded_panel[-1], channel)
        else:
            for dimension in dimensions:
                self.update_panel(dimension, channel)

    def update_panel(self, dimension, channel=0):
        """
        Update the view for a specific dimension and channel.

        Args:
            dimension (str): The dimension to update ("x", "y", or "z").
            channel (int): The modality channel index.
        """
        panel_map = {"x": self.view.panel1, "y": self.view.panel2, "z": self.view.panel4}
        slice_data = self.file_handler.get_slice(dimension, self.file_handler.current_slice[dimension], channel)
        mask_data = self.file_handler.get_mask_slice(dimension, self.file_handler.current_slice[dimension]) if self.file_handler.nii_mask is not None else None
        if slice_data is not None:
            self.view.update_slice(panel_map[dimension], slice_data, self.file_handler.get_current_slice_index(dimension), mask_data, self.selection_list)

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
        self.view.modality_menu.setEnabled(True)

    def change_modality(self, channel):
        """
        Change the current modality channel and update the view.

        Args:
            channel (int): The modality channel index.
        """
        self.file_handler.current_modality_channel = channel
        self.update_panels(self.file_handler.current_modality_channel)

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

    def update_mask_menu(self):
        """
        Update the mask menu with available masks from the NIfTI data.
        """
        self.view.mask_menu.clear()
        self.view.mask_group = QActionGroup(self.view.mask_menu)
        self.view.mask_group.setExclusive(False)

        all_action = QAction("All", self.view)
        all_action.setCheckable(True)
        all_action.setChecked(self.file_handler.show_mask[0])
        all_action.triggered.connect(lambda checked: self.toggle_show_mask(0))
        self.view.mask_group.addAction(all_action)
        self.view.mask_menu.addAction(all_action)

        for i in range(1, self.file_handler.nii_mask_channels):
            action = QAction(str(i), self.view)
            action.setCheckable(True)
            action.setChecked(self.file_handler.show_mask[i])
            action.setEnabled(not self.file_handler.show_mask[0])
            action.triggered.connect(lambda checked, i=i: self.toggle_show_mask(i))
            self.view.mask_group.addAction(action)
            self.view.mask_menu.addAction(action)
        self.view.mask_menu.setEnabled(True)
        
    def update_list_view(self):
        """
        Update the list view with the current selection list.
        """
        self.view.list_view.clear()
        for item in self.selection_list:
            text = f"slice: {item[0]}, layer: {item[1]}, x: {item[2]}, y: {item[3]}, Type: {item[4]}"
            list_item = QListWidgetItem(text)
            self.view.list_view.addItem(list_item)

    def start_segmentation(self):
        """
        Performs segmentation on the selected file and points and saves the results.
        """
        data = self.file_handler.nii_data
        if data is not None:
            output_folder = self.segmentation_output_dir
            scan_name = os.path.basename(self.file_handler.file_path)
            self.data_manager.process_all_scans(data, output_folder, scan_name, image_format="jpeg")
            
            predictor = self.model_manager.get_predictor()
            seg_model = SamModel(predictor, output_folder, scan_name)

            grouped_selection = defaultdict(list)
            for selection in self.selection_list:
                dimension, current_slice, pixel_x, pixel_y, label = selection
                grouped_selection[(dimension, current_slice)].append((pixel_x, 240-pixel_y, label))

            with tqdm(total=len(self.selection_list), desc="Processing selections") as pbar:
                for (dimension, current_slice), points_info in grouped_selection.items():
                    for modality in range(1, self.file_handler.nii_data.shape[3]):
                        seg_model.process_dimension(
                            dimension=dimension,
                            current_slice=current_slice,
                            points_info=points_info,
                            modality=modality
                        )
                    pbar.update(len(points_info))
            
            print("Exporting to NIfTI...")
            seg_model.export_to_nifti()
            print("Segmentation complete and exported.")
        else:
            print("No file selected. Please provide a valid file.")

