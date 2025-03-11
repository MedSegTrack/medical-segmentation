from collections import OrderedDict

import numpy as np
from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtGui import QColor

from gui.filepopup import LoadFileDialog
from gui.guiview import (
    GUI,
    LEFT_SPLITTER_SIZES,
    MAIN_SPLITTER_SIZES,
    RIGHT_SPLITTER_SIZES,
)
from model.data_manager import DataManager

# IMPORTANT: "_" in front of method name is case of this file,
# means that this method should not be manually called,
# that does not include code that already exists in this file. Thanks


class GUIController(QObject):
    s_current_slice_changed = pyqtSignal(str)
    s_panel_toggled_on = pyqtSignal(str)
    s_panel_toggled_off = pyqtSignal()

    def __init__(self, data_manager: DataManager, view: GUI):
        super().__init__()
        self.view = view
        self.data_manager = data_manager
        self.current_slice = {"x": 0, "y": 0, "z": 0}
        self.sliders = OrderedDict(
            {
                "x": self.view.x_slice_slider,
                "y": self.view.y_slice_slider,
                "z": self.view.z_slice_slider,
            }
        )

        self.panels = OrderedDict(
            {
                "x": self.view.panelX,
                "y": self.view.panelY,
                "z": self.view.panelZ,
                "3d": self.view.panel3D,
            }
        )

        self.slider_labels = {
            "x": self.view.x_slice_label,
            "y": self.view.y_slice_label,
            "z": self.view.z_slice_label,
        }

        self.panel_sizes = {
            "x": {
                "main_sizes": [800, 0, 200],
                "left_sizes": [600, 0],
                "right_sizes": None,
            },
            "z": {
                "main_sizes": [800, 0, 200],
                "left_sizes": [0, 600],
                "right_sizes": None,
            },
            "y": {
                "main_sizes": [0, 800, 200],
                "left_sizes": None,
                "right_sizes": [600, 0],
            },
            "3d": {
                "main_sizes": [0, 800, 200],
                "left_sizes": None,
                "right_sizes": [0, 600],
            },
        }

        self.masks_visible = {
            "x": False,
            "y": False,
            "z": False,
        }

        self.mask_color_map = {
            1: QColor(0, 0, 255, 100),
            2: QColor(255, 0, 0, 100),
            3: QColor(255, 165, 0, 100),
        }

        self.voxel_mapping = {
            "x": lambda v: (v.y, v.z, v.x),
            "y": lambda v: (v.x, v.z, v.y),
            "z": lambda v: (v.x, v.y, v.z),
        }

        self.current_modality_channel = 0
        self.number_of_mask_channels = 0
        self.selection_list = []

        self.current_expanded_panel = None

        self.layers_locked_checked = False
        self.selection_mode_checked = False

        self._connect_actions()
        self._connect_signals()

    def _connect_signals(self):
        """
        Helper method to connect controller specific signals to slots.
        """

        self.s_panel_toggled_on.connect(self._fs_sliders_disable)
        self.s_panel_toggled_on.connect(self._fs_expand_panel)

        self.s_panel_toggled_off.connect(self._fs_sliders_enable)
        self.s_panel_toggled_off.connect(self._fs_collapse_panel)

        self.s_current_slice_changed.connect(self._fs_update_slice)
        self.s_current_slice_changed.connect(self._fs_update_slider)

    def _connect_actions(self):
        """
        Helper method to connect slots to UI actions.
        """
        # File menu actions
        self.view.exit_action.triggered.connect(self._fs_close_app)
        self.view.load_action.triggered.connect(self._fs_load_files)
        self.view.save_action.triggered.connect(self._fs_save_files)

        # Settings menu actions
        self.view.lock_layers_action.triggered.connect(self.toggle_lock_layers)
        self.view.disable_3d_panel_action.triggered.connect(
            self.toggle_disable_3d_panel
        )

        # Side panel
        self.view.reset_selection_button.clicked.connect(self.reset_selection)
        self.view.checkbox_selection_mode.stateChanged.connect(
            self.toggle_selection_mode
        )

        for dim, slider in self.sliders.items():
            slider.valueChanged.connect(
                lambda value, d=dim: self._fs_on_slider_value_changed(d, value)
            )

    def _connect_panel_mouse_events(self):
        """
        Helper method to connect mouse events on panels.
        """
        for dim, panel in self.panels.items():
            panel.mouseDoubleClickEvent = (
                lambda event, d=dim: self._fs_toggle_expanded_panel(d, event)
            )
            if dim != "3d":
                panel.wheelEvent = lambda event, d=dim: self._fs_scroll_slice(d, event)
                panel.mousePressEvent = lambda event, d=dim: self.mouse_click_selection(
                    d, event
                )

    def _fs_on_slider_value_changed(self, dim, value):
        """
        Helper slot called when the value of a slider is changed.
        Propagates the change to the current_slice.
        """
        self.set_current_slice(**{dim: value})

    def _fs_close_app(self):
        """
        Slot called after user exits the program.
        """
        self.view.close()

    def _fs_load_files(self):
        """
        Slot called to load a dialog to load a NIfTI file and optionally a NIfTI mask file.
        Update the view with the loaded data.

        Raises:
            Exception: If an error occurs while loading the NIfTI file or mask.
        """
        dialog = LoadFileDialog()
        if dialog.exec_():
            try:
                self.data_manager.mask_loader = None
                self.data_manager.image_loader = None
                if hasattr(dialog, "nifti_path"):
                    self.data_manager.load_image(dialog.nifti_path)
                    self._update_after_file_load()

                if dialog.checkbox.isChecked() and hasattr(dialog, "mask_path"):
                    self.data_manager.load_mask(dialog.mask_path)

            except Exception as e:
                self.view.display_error_message(f"Failed to load files: {str(e)}")

    def _fs_save_files(self):
        print("Saving files")

    def set_current_slice(self, **kwargs):
        """
        Method to change the index of currently displayed slice,
        emits s_current_slice_changed signal.
        """
        for dim, val in kwargs.items():
            if dim in self.current_slice and self.current_slice[dim] != val:
                self.current_slice[dim] = val
                self.s_current_slice_changed.emit(dim)

    def toggle_lock_layers(self):
        """
        Slot called to toggle state of layers_locked
        """
        self.layers_locked_checked = self.view.lock_layers_action.isChecked()

    def toggle_disable_3d_panel(self):
        print("Disabling 3d panel")

    def reset_selection(self):
        # TODO 2
        print("Selection reset")

    def _fs_update_selection_list_view(self):
        # TODO 1
        print("updating selection")

    def toggle_selection_mode(self):
        self.selection_mode_checked = self.view.checkbox_selection_mode.isChecked()

    def _fs_toggle_expanded_panel(self, dim, event):
        """
        Slot called when panel is expanded,
        emits s_panel_toggled_off/on depending on the action.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_expanded_panel != dim:
                self.current_expanded_panel = dim
                self.s_panel_toggled_on.emit(dim)
            else:
                self.current_expanded_panel = None
                self.s_panel_toggled_off.emit()

    def _fs_scroll_slice(self, dim, event):
        """
        Slot called when mouse scroll action is performed, changes current_slice
        index depending on y direction of scroll movement.

        Args:
            dim (str): Dimension index of the slice which contains the scroll event
            event (Qt.Event): Scroll event
        """
        scroll_amount = 1 if event.angleDelta().y() > 0 else -1
        if self.current_expanded_panel is None and self.layers_locked_checked is True:
            cx, cy, cz = (
                self.current_slice[k] + scroll_amount for k in ("x", "y", "z")
            )
            self.set_current_slice(x=cx, y=cy, z=cz)
        else:
            cd = self.current_slice[dim] + scroll_amount
            self.set_current_slice(**{dim: cd})

    def mouse_click_selection(self, dim, event):
        # TODO 0
        print("Mouse click selecting")

    def _update_ui_visibility(self):
        """
        Helper method to set ui elemets visible, after loading a file
        """
        self.view.lock_layers_action.setEnabled(True)
        self.view.disable_3d_panel_action.setEnabled(True)
        self.view.reset_layers_button.setEnabled(True)

    def _update_after_file_load(self):
        """
        Method to perform initial update after loading the file
        """
        image_data = self.data_manager.get_image_data()
        if image_data is not None and image_data.shape is not None:
            self.set_current_slice(
                x=image_data.shape[0] // 2,
                y=image_data.shape[1] // 2,
                z=image_data.shape[2] // 2,
            )

            for index, (_, slider) in enumerate(self.sliders.items()):
                slider.setMinimum(0)
                slider.setMaximum(image_data.shape[index] - 1)

            self._connect_panel_mouse_events()
            self._update_ui_visibility()
            self._fs_sliders_enable()

    def _fs_update_slider(self, dim):
        """
        Slot called when value and label of a selected slider.

        Args:
            dim (str): Dimension index of the slider to update
        """
        self.slider_labels[dim].setText(f"{dim.upper()}: {self.current_slice[dim]}")
        self.sliders[dim].setValue(self.current_slice[dim])

    def _fs_sliders_disable(self, dim):
        """
        Slot called to disable panels which are not visible,
        i.e when a panel is expanded.

        Args:
            dim (str): Dimension index of visible panel
        """
        for _, slider in self.sliders.items():
            slider.setEnabled(False)
        if dim != "3d":
            self.sliders[dim].setEnabled(True)

    def _fs_sliders_enable(self):
        """
        Slot called after restoring UI to original state with all panels visible.
        """
        for _, slider in self.sliders.items():
            slider.setEnabled(True)

    def _fs_expand_panel(self, dim):
        """
        Slot called to change visible UI layout after expanding a panel.

        Args:
            dim (str): Dimension index of currently expanded panel
        """
        self.view.main_splitter.setSizes(self.panel_sizes[dim]["main_sizes"])
        left_sizes = self.panel_sizes[dim]["left_sizes"]
        right_sizes = self.panel_sizes[dim]["right_sizes"]
        if left_sizes:
            self.view.left_splitter.setSizes(left_sizes)
        else:
            self.view.right_splitter.setSizes(right_sizes)

    def _fs_collapse_panel(self):
        """
        Slot called to collapse currently expanded panel, restoring original UI layout
        """
        self.view.main_splitter.setSizes(MAIN_SPLITTER_SIZES)
        self.view.left_splitter.setSizes(LEFT_SPLITTER_SIZES)
        self.view.right_splitter.setSizes(RIGHT_SPLITTER_SIZES)

    def _fs_update_slice(self, dim):
        """
        Slot called to update the slice displayed on the panel,
        after current_slice is changed.

        Creates a new FigureCanvas on which the slice and optionally mask and selection_points are plotted.
        Calls the draw function direcly on the View object.

        Args:
            dim (str): The dimension index of the panel to update
        """
        fig = self.panels[dim].figure
        fig.texts.clear()
        fig.text(
            0.05, 0.05, dim.upper(), color="white", fontsize=12, ha="left", va="bottom"
        )
        fig.text(
            0.95,
            0.05,
            f"Slice: {self.current_slice[dim]}",
            color="white",
            fontsize=12,
            ha="right",
            va="bottom",
        )
        ax = fig.gca()
        ax.clear()

        new_image_array = self.get_current_slice_or_mask(
            dim, is_mask=False
        ).get_image_as_array()
        w, h = new_image_array.shape
        extent = (0, w, h, 0)
        ax.imshow(
            np.rot90(new_image_array, 1), cmap="grey", aspect="equal", extent=extent
        )

        if True in self.masks_visible:
            color_mask_array = self.get_colored_mask(dim)
            if color_mask_array is not None:
                ax.imshow(
                    np.rot90(color_mask_array, 1),
                    alpha=0.4,
                    extent=extent,
                    aspect="equal",
                )

        if self.selection_list:
            for voxel, t in self.selection_list:
                x, y, z = self.voxel_mapping[dim](voxel)
                if z == self.current_slice[dim]:
                    marker = "go" if t == "P" else "ro"
                    ax.plot(x, h - y, marker)

        ax.axis("off")
        self.panels[dim].draw()

    def get_current_slice_or_mask(self, dim, is_mask):
        """
        Method returning the slice or mask for the slice from the data_manager

        Args:
            dim (str): Dimension Index of the slice/mask)
        Returns:
            Slice object?
        """
        return self.data_manager.get_image_slice(
            dim, self.current_modality_channel, self.current_slice[dim], is_mask
        )

    def get_colored_mask(self, dim):
        """
        Method to a slice of the Nifti mask data along a given dimension index with colors.

        Slice is unwrapped into a 3D array with ARGB colors.

        Args:
            dim (str): "x", "y", or "z" indicating the slice direction.

        Returns:
            np.ndarray: Colored mask slice, or None if invalid input.
        """
        mask_data = self.data_manager.get_mask_data()
        if mask_data is not None and mask_data.shape is not None:
            dim_map = {"x": 0, "y": 1, "z": 2}
            if (
                dim not in dim_map
                or self.current_slice[dim] >= mask_data.shape[dim_map[dim]]
            ):
                return None

            mask_slice = self.get_current_slice_or_mask(dim, True)
            colored_mask = np.zeros((*mask_slice.shape, 4))

            for i, show in enumerate(self.masks_visible):
                if show:
                    colored_mask[mask_slice == i] = self.get_mask_color(i)

            return colored_mask
        return None

    def _create_mask_menu(self):
        print("creating_mask menu")

    def get_mask_color(self, channel):
        """
        Helper method to get the color associated with a given mask channel.

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
