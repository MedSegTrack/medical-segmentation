from PyQt5.QtWidgets import QAction, QActionGroup, QListWidgetItem, QProgressDialog
from PyQt5.QtCore import Qt, QEvent
from gui.view import MAIN_SPLITTER_SIZES, LEFT_SPLITTER_SIZES, RIGHT_SPLITTER_SIZES
from gui.filepopup import LoadFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import vedo
from functools import partial

from segmentation.segmentationController import SegmentationController
from .segmentation_worker import SegmentationWorker

import os

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

        self.segmentation_controller = None

        try:
            self.segmentation_controller = SegmentationController(self.data_manager)
            self.segmentation_controller.initialize_model()
        except Exception as e:
            print(f"Warning: Could not initialize segmentation controller: {e}")


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

        self.view.run_segmentation_button.clicked.connect(self.start_segmentation)

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
        self.update_3d_view()

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
        if self.expanded_panel != "Panel-3d" and self.expanded_panel is not None:
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
        mask_data = None
        if self.data_manager.get_mask_data() is not None:
            mask_data = self.get_colored_mask(dimension, self.current_slice[dimension])
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
        # Retrieve volume and mask data
        image_data_obj = self.data_manager.get_image_data()
        volume_data = image_data_obj.data if image_data_obj is not None else None
        mask_data_obj = self.data_manager.get_mask_data()
        mask_data = mask_data_obj.data if mask_data_obj is not None else None

        if volume_data is None:
            return

        # Ensure volume data is a numpy array and handle 4D data by selecting the modality channel
        volume_data = np.array(volume_data)
        if volume_data.ndim == 4:
            volume_data = volume_data[..., self.current_modality_channel]

        # Create the volume actor and prepare the plotter
        volume = vedo.Volume(volume_data)
        plotter = self.view.get_vedo_plotter()
        plotter.clear()
        actors = [volume]

        # Helper function to create a small volumetric sphere at the voxel location.
        def create_voxel_sphere(voxel, vol_data, marker_type):
            sphere_vol = np.zeros_like(vol_data)
            x, y, z = int(voxel.x), int(voxel.y), int(voxel.z)
            sphere_vol[x - 1: x + 2, y - 1: y + 2, z - 1: z + 2] = 1  # 3x3x3 cube pattern
            vsphere = vedo.Volume(sphere_vol)
            color = [(1,[0, 1, 0])] if marker_type == "P" else [(2, [1, 0, 0])]
            vsphere.cmap(color)
            return vsphere

        # If any masks should be shown, process and add the mask volume.
        if self.show_mask != [False] * self.mask_channels:
            if mask_data is not None:
                mask_data = np.array(mask_data)
                if mask_data.ndim == 4:
                    mask_data = mask_data[..., 0]

                # Determine which mask values to display.
                masks_to_show = [1, 2, 3] if self.show_mask[0] else [i + 1 for i, visible in enumerate(self.show_mask[1:]) if visible]
                # Use vectorized operation to keep only the selected mask values.
                processed_mask = np.where(np.isin(mask_data, masks_to_show), mask_data, 0)
                mask_volume = vedo.Volume(processed_mask)
                # Custom colormap: 0-transparent, 1-blue, 2-red, 3-yellow
                colors = [
                    (0, [0, 0, 0]),
                    (1, [0, 0, 1]),
                    (2, [1, 0, 0]),
                    (3, [1, 1, 0]),
                ]
                mask_volume.cmap(colors)
                actors.append(mask_volume)

        if self.selection_list:
            for voxel, marker_type in self.selection_list:
                actors.append(create_voxel_sphere(voxel, volume_data, marker_type))

        plotter.show(actors, axes=None, viewup="z", bg='black', title='3D View', bg2='black')

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
        
    def start_segmentation(self):
        """Start segmentation process with selected points."""
        if not self.data_manager.image_loader:
            self.view.display_error("No image loaded")
            return
            
        if not self.selection_list:
            self.view.display_error("No points selected")
            return

        if not self.segmentation_controller:
            self.view.display_error("Segmentation model not initialized")
            return

        try:
            # Group selections by slice
            grouped_selections = self._group_selections()
            if not grouped_selections:
                self.view.display_error("No valid selections found")
                return

            # Create progress dialog
            self._progress_dialog = QProgressDialog("Preparing for segmentation...", None, 0, 100, self.view)
            self._progress_dialog.setWindowModality(Qt.WindowModal)
            self._progress_dialog.setAutoClose(True)
            self._progress_dialog.setMinimumDuration(0)
            
            # Connect cancel button
            self._progress_dialog.canceled.connect(self._cancel_segmentation)
            

            # Create and configure worker
            self.segmentation_worker = SegmentationWorker(
                self.segmentation_controller,
                grouped_selections,
                'z'
            )

            # Connect signals
            self.segmentation_worker.finished.connect(
                lambda masks: self._handle_segmentation_complete(masks, self._progress_dialog)
            )
            self.segmentation_worker.progress.connect(self._progress_dialog.setValue)
            self.segmentation_worker.status.connect(self._progress_dialog.setLabelText)  # Connect status updates
            self.segmentation_worker.error.connect(
                lambda err: self._handle_segmentation_error(err, self._progress_dialog)
            )

            self._progress_dialog.show()
            # Start worker
            self.segmentation_worker.start()    

        except Exception as e:
            self.view.display_error(f"Failed to start segmentation: {str(e)}")

    def _cancel_segmentation(self):
        """Cancel ongoing segmentation."""
        try:
            # Cancel the segmentation in the controller
            if self.segmentation_controller:
                self.segmentation_controller.cancel_segmentation()
            
            # Stop and clean up the worker
            if hasattr(self, 'segmentation_worker') and self.segmentation_worker is not None:
                self.segmentation_worker.quit()
                self.segmentation_worker.wait()  # Wait for the thread to finish
                self.segmentation_worker = None
            
            # Close the progress dialog
            if hasattr(self, '_progress_dialog') and self._progress_dialog is not None:
                self._progress_dialog.close()  # Use close() instead of hide()
                self._progress_dialog = None
                
        except Exception as e:
            print(f"Error during cancellation: {e}")

    def _handle_segmentation_complete(self, masks, progress):
        """Handle completion of segmentation."""
        progress.close()
        
        if masks:
            self.find_mask_channels()
            self.show_mask = [False] * self.mask_channels
            self.show_mask[1] = True
            self.update_mask_menu()
            self.update_panels()
            self.update_3d_view()
        else:
            self.view.display_error("No masks generated")

    def _handle_segmentation_error(self, error_msg, progress):
        """Handle segmentation error."""
        progress.close()
        self.view.display_error(f"Segmentation failed: {error_msg}")

    def _group_selections(self):
        """Group selection points by slice index.
        
        Returns:
            Dict[int, List[Tuple[int, int, str]]]: Dictionary mapping slice indices to lists of (x, y, label) tuples
        """
        grouped = {}
        for voxel, label in self.selection_list:
            # Use z coordinate as slice index
            slice_idx = voxel.z
            
            if slice_idx not in grouped:
                grouped[slice_idx] = []
                
            # Store x, y coordinates and label
            grouped[slice_idx].append(
                (voxel.x, self.data_manager.image.shape[0]-voxel.y, label)
            )
        
        return grouped