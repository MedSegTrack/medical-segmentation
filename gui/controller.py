from PyQt5.QtWidgets import QAction, QActionGroup, QListWidgetItem
from PyQt5.QtCore import Qt, QEvent
from gui.view import MAIN_SPLITTER_SIZES, LEFT_SPLITTER_SIZES, RIGHT_SPLITTER_SIZES
from gui.filepopup import LoadFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import vedo
from vedo import Volume, Plotter, merge
from functools import partial

import numpy as np
class GuiController:
    """
    Controller class to manage interactions between the GUI view and the file_handler.
    """
    def __init__(self, data_manager, view):
        """
        Initialize the GUI Controller.

        Args:
            filehandler: The data filehandler containing the application's state and data.
            view: The GUI view for displaying and interacting with the user.
        """

        self.data_manager = data_manager
        self.view = view
        self.is_layers_locked = False
        self.expanded_panel = None
        self.is_updating_slider = False
        self.selection_list = []
        self.is_selection_mode = False
        self.current_slice = {"x": 0, "y": 0, "z": 0}
        self.current_modality_channel = 0
        self.show_mask = []
        self.mask_channels = 0

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

        self.view.list_view.itemClicked.connect(self.on_list_item_selected)

    def _connect_panel_events(self):
        """Connect panel-specific mouse and wheel events."""
        for dimension, panel in zip(["x", "y", "z"], [self.view.panel1, self.view.panel2, self.view.panel4]):
            panel.mouseDoubleClickEvent = lambda event, dim=dimension: self.toggle_panel(f"Panel-{dim}")
            panel.wheelEvent = lambda event, dim=dimension: self.scroll_slice(dim, event.angleDelta().y())
            panel.mousePressEvent = lambda event, dim=dimension: self.mouse_click_selection(event, dim)

    def update_sliders(self):
        """
        Update the slice sliders based on the current image data shape and the current slice index.
        """
        dimension = ['x', 'y', 'z']
        for dim in dimension:
            slider = getattr(self.view, f"{dim}_slice_slider")
            slider.setMinimum(0)
            slider.setMaximum(self.data_manager.get_image_data().shape[dimension.index(dim)] - 1)
            slider.setValue(self.current_slice[dim])
            if self.expanded_panel is None:
                slider.setEnabled(True)
            else:
                slider.setEnabled(False)
        if self.expanded_panel is not None and self.expanded_panel[-1] in dimension:
            cur_slider = getattr(self.view, f"{self.expanded_panel[-1]}_slice_slider")
            cur_slider.setEnabled(True)

    def clear_selection_list(self):
        """
        Clear the selection list.
        """
        self.selection_list = []
        self.update_panels()
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
        if self.data_manager.get_image_data() is None or not self.is_selection_mode:
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
            current_slice = self.get_current_slice(dimension, self.current_slice[dimension])
        

            shape_x, shape_y = current_slice.shape
            # Calculate pixel values
            pixel_x = int((image_x - left) / img_width * shape_x)
            pixel_y = int((image_y - bottom) / img_height * shape_y)

            selected_voxel = current_slice.get_voxel(pixel_x, pixel_y)

            if event.button() == Qt.LeftButton:
                self.selection_list.append((selected_voxel, "P"))
            elif event.button() == Qt.RightButton:
                self.selection_list.append((selected_voxel, "N"))

            self.update_panels()
            self.update_list_view()
            self.update_3d_view()

    def toggle_show_mask(self, mask_index):
        """
        Toggle the mask visibility in the view.
        
        Args:
            mask_index (int): The index of the mask to toggle. 0 toggles all masks
        """
        def toggle_all_masks(state):
            self.show_mask = [state] * self.mask_channels
        
        if mask_index == 0:
            # Toggle all masks
            new_state = not all(self.show_mask)
            toggle_all_masks(new_state)
        else:
            self.show_mask[mask_index] = not self.show_mask[mask_index]
            self.show_mask[0] = False

        self.update_mask_menu()
        self.update_panels()
        self.update_3d_view()

    def on_slider_value_changed(self, dimension, value):
        """
        Handles the slider value change event and updates the current slice.
        """
        if not self.is_updating_slider:
            self.is_updating_slider = True  # Prevent recursion

            self.current_slice[dimension] = value
            self.update_panels()
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
        if self.data_manager.get_image_data() is not None:
            self.current_slice = {"x": self.data_manager.get_image_data().shape[0] // 2, "y": self.data_manager.get_image_data().shape[1] // 2, "z": self.data_manager.get_image_data().shape[2] // 2}
            self.update_panels()
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
                    self.current_slice[dim] = max(self.current_slice[dim] - 1, 0)
                else:
                    self.current_slice[dim] = min(self.current_slice[dim] + 1,
                                                            self.data_manager.get_image_data().shape[{"x": 0, "y": 1, "z": 2}[dim]] - 1)
                getattr(self.view, f"{dim}_slice_slider").setValue(self.current_slice[dim])
                getattr(self.view, f"{dim}_slice_label").setText(f"{dim.upper()}: {self.current_slice[dim]}")

        if self.data_manager.get_image_data() is not None:
            self.is_updating_slider = True
            if self.is_layers_locked and self.expanded_panel is None:
                update_current_slices(["x", "y", "z"])
            else:
                update_current_slices([dimension])
            self.update_panels()
            self.is_updating_slider = False

    def toggle_dark_mode(self):
        """
        Toggle between dark mode and light mode in the view.
        """
        if self.view.dark_mode_action.isChecked():
            self.view.apply_dark_mode()
        else:
            self.view.apply_light_mode()

    def toggle_panel(self, panel_name, event=None):
        """
        Toggle the expansion state of a specific panel.

        Args:
            panel_name (str): The name of the panel to toggle.
        """
        if self.data_manager.get_image_data() is None:
            return
        
        if self.expanded_panel == panel_name:
            # Reset to default layout
            self.view.main_splitter.setSizes(MAIN_SPLITTER_SIZES)
            self.view.left_splitter.setSizes(LEFT_SPLITTER_SIZES)
            self.view.right_splitter.setSizes(RIGHT_SPLITTER_SIZES)
            self.reset_expanded_panel()
            self.update_panels()
            self.view.x_slice_slider.setEnabled(True)
            self.view.y_slice_slider.setEnabled(True)
            self.view.z_slice_slider.setEnabled(True)
        else:
            # Expand the selected panel
            if panel_name == "Panel-x":
                self.view.main_splitter.setSizes([800, 0, 200])
                self.view.left_splitter.setSizes([600, 0])
                if self.data_manager.get_image_data() is not None:
                    self.view.x_slice_slider.setEnabled(True)
                    self.view.y_slice_slider.setEnabled(False)
                    self.view.z_slice_slider.setEnabled(False)
            elif panel_name == "Panel-z":
                self.view.main_splitter.setSizes([800, 0, 200])
                self.view.left_splitter.setSizes([0, 600])
                if self.data_manager.get_image_data() is not None:
                    self.view.x_slice_slider.setEnabled(False)
                    self.view.y_slice_slider.setEnabled(False)
                    self.view.z_slice_slider.setEnabled(True)
            elif panel_name == "Panel-y":
                self.view.main_splitter.setSizes([0, 800, 200])
                self.view.right_splitter.setSizes([600, 0])
                if self.data_manager.get_image_data() is not None:
                    self.view.x_slice_slider.setEnabled(False)
                    self.view.y_slice_slider.setEnabled(True)
                    self.view.z_slice_slider.setEnabled(False)
            elif panel_name == "Panel-3d":
                self.view.main_splitter.setSizes([0, 800, 200])
                self.view.right_splitter.setSizes([0, 600])
                if self.data_manager.get_image_data() is not None:
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
                self.data_manager.mask_loader = None
                self.data_manager.image_loader = None
                # Load the primary NIfTI file
                if hasattr(dialog, 'nifti_path'):
                    self.data_manager.load_image(dialog.nifti_path)
                    self.update_modality_menu()
                    self.update_sliders()
                # Load the optional mask file if the checkbox is checked
                if dialog.checkbox.isChecked() and hasattr(dialog, 'mask_path'):
                    self.data_manager.load_mask(dialog.mask_path)
                    self.find_mask_channels()
                    self.update_mask_menu()
                
                self.current_slice = {"x": self.data_manager.get_image_data().shape[0] // 2, "y": self.data_manager.get_image_data().shape[1] // 2, "z": self.data_manager.get_image_data().shape[2] // 2}
                self.update_panels()
                self.update_sliders()
                self.update_3d_view()
                self.view.get_vedo_plotter().add_callback("RightButtonPressEvent", partial(self.toggle_panel, "Panel-3d"))
                
            except Exception as e:
                self.view.display_error(f"Failed to load files: {str(e)}")

    def update_panels(self, dimensions=["x", "y", "z"]):
        """
        Update all slice views for given dimensions and modality channel.

        Args:
            dimensions (list): List of dimensions to update.
            channel (int): The modality channel index.
        """
        if self.expanded_panel != "Panel-3d":
            if self.expanded_panel is not None:
                self.update_panel(self.expanded_panel[-1])
            else:
                for dimension in dimensions:
                    self.update_panel(dimension)

    def update_panel(self, dimension):
        """
        Update the view for a specific dimension and channel.

        Args:
            dimension (str): The dimension to update ("x", "y", or "z").
            channel (int): The modality channel index.
        """
        panel_map = {"x": self.view.panel1, "y": self.view.panel2, "z": self.view.panel4}
        slice_data = self.get_current_slice(dimension, self.current_slice[dimension])
        mask_data = self.get_colored_mask(dimension, self.current_slice[dimension]) if self.data_manager.get_mask_data() is not None else None
        if slice_data is not None:
            self.view.update_slice(panel_map[dimension], slice_data, self.current_slice[dimension], mask_data, self.selection_list)

    def update_modality_menu(self):
        """
        Update the modality menu with available channels from the NIfTI data.
        """
        self.view.modality_menu.clear()
        self.view.modality_group = QActionGroup(self.view.modality_menu)
        self.view.modality_group.setExclusive(True)
        for i in (self.data_manager.get_image_data().modalities):
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
        self.current_modality_channel = channel
        self.update_panels()
        self.update_3d_view()

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
        all_action.setChecked(self.show_mask[0])
        all_action.triggered.connect(lambda checked: self.toggle_show_mask(0))
        self.view.mask_group.addAction(all_action)
        self.view.mask_menu.addAction(all_action)

        for i in range(1, self.mask_channels):
            action = QAction(str(i), self.view)
            action.setCheckable(True)
            action.setChecked(self.show_mask[i])
            action.setEnabled(not self.show_mask[0])
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
            text = f"{item[0]}, Type: {item[1]}"
            list_item = QListWidgetItem(text)
            self.view.list_view.addItem(list_item)

    def get_current_slice(self, dimension, slice_index):
        """
        Get a slice of the Nifti data along a given dimension.
        
        Args:
            dimension (str): "x", "y", or "z" indicating the slice direction.
            slice_index (int): Index of the slice to extract.
            
        Returns:
            Slice object, None otherwise: Image slice, or None if invalid input.
        """
        return self.data_manager.get_image_slice(dimension, self.current_modality_channel, slice_index)

    def get_current_mask(self, dimension, index):
        """
        Get a slice of the Nifti mask data along a given dimension.
        
        Args:
            dimension (str): "x", "y", or "z" indicating the slice direction.
            index (int): Index of the slice to extract.
            
        Returns:
            Slice object, None otherwise: Mask slice, or None if invalid input.
        """
        return self.data_manager.get_image_slice(dimension, self.current_modality_channel, index, is_mask=True)
    
    def get_colored_mask(self, dimension, index):
        """
        Get a slice of the Nifti mask data along a given dimension with colors.
        Slice is unwrapped into a 3D array with ARGB colors.

        Args:
            dimension (str): "x", "y", or "z" indicating the slice direction.
            index (int): Index of the slice to extract.
        
        Returns:
            np.ndarray: Colored mask slice, or None if invalid input.
        """
        mask_data = self.data_manager.get_mask_data()
        if mask_data is None:
            return None

        dim_map = {"x": 0, "y": 1, "z": 2}
        if dimension not in dim_map or index >= mask_data.shape[dim_map[dimension]]:
            return None

        mask_slice = self.get_current_mask(dimension, index).get_image_as_array()
        colored_mask = np.zeros((*mask_slice.shape, 4))

        for i, show in enumerate(self.show_mask):
            if show:
                colored_mask[mask_slice == i] = self.get_mask_color(i)

        return colored_mask

    def find_mask_channels(self):
        """
        Find the number of channels in the mask data.
        """
        unique_values = np.unique(self.data_manager.get_mask_data().data.astype(int))
        self.mask_channels = len(unique_values)
        self.show_mask = [False] * self.mask_channels
        
    def get_mask_color(self, channel):
        """
        Get the color associated with a given mask channel.

        Args:
            channel (int): Channel for which to get the color

        Returns:
            tuple: ARGB color associated with the given channel
        """
        if channel == 1:
            return (0, 0, 1, 1)
        elif channel == 2:
            return (1, 0, 0, 1)
        elif channel == 3:
            return (1, 1, 0, 1)
        else:
            return (0, 0, 0, 0)

    def update_3d_view(self):
        """
        Update the 3D view with the current volume data and overlay the mask data.
        """
        volume_data = self.data_manager.get_image_data().data  # Get full image data
        mask_data = self.data_manager.get_mask_data().data if self.data_manager.get_mask_data() is not None else None

        if volume_data is not None:
            volume_data = np.array(volume_data)
            # Handle 4D data by selecting the current modality channel
            if len(volume_data.shape) == 4:
                volume_data = volume_data[..., self.current_modality_channel]
            volume = vedo.Volume(volume_data)
            self.view.get_vedo_plotter().clear()

            actors = [volume]
            
            if self.show_mask == [False] * self.mask_channels:
                if self.selection_list:
                    for voxel, type in self.selection_list:
                        # Create a small volumetric sphere (3x3x3 voxels)
                        sphere_vol = np.zeros_like(volume_data)
                        
                        # Create spherical pattern at target coordinates
                        x, y, z = int(voxel.x), int(voxel.y), int(voxel.z)
                        sphere_vol[x-1:x+2, y-1:y+2, z-1:z+2] = 1  # Simple 3x3x3 cube
                        # For better sphere shape (5x5x5):
                        # sphere_vol[x-2:x+3, y-2:y+3, z-2:z+3] = create_sphere_kernel()
                        
                        # Create volume with custom color/opacity
                        vsphere = vedo.Volume(sphere_vol)
                        color = [0, 1, 0] if type == "P" else [1, 0, 0]  # RGB colors
                        vsphere.cmap(color)
                        
                        actors.append(vsphere)
                self.view.get_vedo_plotter().show(actors, axes=None, viewup="z", bg='black', title = '3D View', bg2='black')
            else:
                if mask_data is not None:
                    mask_data = np.array(mask_data)
                    # Handle 4D mask data by selecting the first channel
                    if len(mask_data.shape) == 4:
                        mask_data = mask_data[..., 0]

                    # Determine which masks to display
                    all_masks_visible = self.show_mask[0]
                    masks_to_show = []
                    if all_masks_visible:
                        masks_to_show = [1, 2, 3]
                    else:
                        masks_to_show = [i+1 for i, visible in enumerate(self.show_mask[1:]) if visible]

                    # Process the mask data to include only selected masks
                    processed_mask = np.zeros_like(mask_data)
                    for mask_value in masks_to_show:
                        processed_mask = np.where(mask_data == mask_value, mask_value, processed_mask)

                    # Create mask volume and apply custom colormap
                    mask_volume = vedo.Volume(processed_mask)
                    # Define custom color map: 0-transparent, 1-blue, 2-red, 3-blue
                    colors = (
                        [
                            (0, [0, 0, 0]),  # Transparent
                            (1, [0, 0, 1]),  # Blue
                            (2, [1, 0, 0]),  # Red
                            (3, [1, 1, 0]),  # Blue
                        ]
                    )
                    mask_volume.cmap(colors)
                    actors.append(mask_volume)
                    if self.selection_list:
                        for voxel, type in self.selection_list:
                            # Create a small volumetric sphere (3x3x3 voxels)
                            sphere_vol = np.zeros_like(volume_data)
                            
                            # Create spherical pattern at target coordinates
                            x, y, z = int(voxel.x), int(voxel.y), int(voxel.z)
                            sphere_vol[x-1:x+2, y-1:y+2, z-1:z+2] = 1  # Simple 3x3x3 cube
                            # For better sphere shape (5x5x5):
                            # sphere_vol[x-2:x+3, y-2:y+3, z-2:z+3] = create_sphere_kernel()
                            
                            # Create volume with custom color/opacity
                            vsphere = vedo.Volume(sphere_vol)
                            color = [0, 1, 0] if type == "P" else [1, 0, 0]  # RGB colors
                            vsphere.cmap(color)
                            
                            actors.append(vsphere)
                    self.view.get_vedo_plotter().show(actors, axes=None, viewup="z", bg='black', title='3D View', bg2='black')

    def on_list_item_selected(self, item):
        """Handle selection of an item in the list view.
        
        Args:
            item (QListWidgetItem): The selected item
        """
        index = self.view.list_view.row(item)
        selected_voxel, selection_type = self.selection_list[index]
        
        self.current_slice = {
            "x": selected_voxel.x,
            "y": selected_voxel.y,
            "z": selected_voxel.z
        }
        
        self.update_sliders()
        self.update_panels()
        
