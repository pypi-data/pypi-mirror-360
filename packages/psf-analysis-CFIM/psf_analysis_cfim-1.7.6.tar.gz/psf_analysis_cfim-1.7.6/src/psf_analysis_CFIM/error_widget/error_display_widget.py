import numpy as np
from qtpy.QtCore import QBuffer, QIODevice
from qtpy.QtCore import QByteArray
from qtpy.QtCore import QObject, Signal
from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QHBoxLayout
from qtpy.QtWidgets import QLabel
from qtpy.QtWidgets import QWidget, QVBoxLayout, QMessageBox

from psf_analysis_CFIM.library_workarounds.QPushButton import RichTextPushButton


def upscale_to_3d(coordinate):
    # If a scalar is given, wrap it in a tuple.
    if isinstance(coordinate, (int, float)):
        coordinate = (coordinate,)
    else:
        coordinate = tuple(coordinate)

    if len(coordinate) == 1:
        # For a 1D coordinate, use (value, 0, 0)
        return coordinate[0], 0, 0
    elif len(coordinate) == 2:
        # For a 2D coordinate, use (0, first, second)
        return 0, coordinate[0], coordinate[1]
    elif len(coordinate) == 3:
        return coordinate
    else:
        raise ValueError("Coordinate must have at most 3 dimensions")

def pixmap_to_html(pixmap, width=16, height=16):
    """Convert a QPixmap to an HTML <img> tag with a base64-encoded PNG."""
    ba = QByteArray()
    buffer = QBuffer(ba)
    buffer.open(QIODevice.WriteOnly)
    pixmap.save(buffer, "PNG")
    buffer.close()
    b64_str = ba.toBase64().data().decode("ascii")
    return f'<img src="data:image/png;base64,{b64_str}" width="{width}" height="{height}">'

def report_error(message="", point=()):
    error_emitter.errorOccurred.emit(message, point)

def report_warning(message="", points=[]):
    error_emitter.warningOccurred.emit(message, points)

class ErrorEmitter(QObject):
    errorOccurred = Signal(str, tuple)
    warningOccurred = Signal(str, list)

error_emitter = ErrorEmitter()

def report_validation_error(message="", channel=0):
    validation_emitter.errorOccurred.emit(message, int(channel))

def report_validation_warning(message="", channel=0):
    validation_emitter.warningOccurred.emit(message, int(channel))

class ValidationErrorEmitter(QObject):
    errorOccurred = Signal(str, int)
    warningOccurred = Signal(str, int)

validation_emitter = ValidationErrorEmitter()


class ErrorDisplayWidget(QWidget):
    def __init__(self, parent=None, viewer=None, scale=(1, 1, 1)):
        """
            Creates a summary of given errors and warnings.
            Summary gives a detail view when clicked.
        """
        super().__init__(parent)
        self.channel_warnings = {}
        self.channel_errors = {}
        self.warnings = []
        self.errors = []
        self.img_index = 0

        self.error_points_layer = None
        self.warning_points_layer = None
        self.shape_layer = None

        self._viewer = viewer
        self._scale = scale

        self.warning_icon = QPixmap("src/psf_analysis_CFIM/error_widget/resources/warning_triangle.png")
        self.error_icon = QPixmap("src/psf_analysis_CFIM/error_widget/resources/error_triangle.png")
        self.warning_icon_html = pixmap_to_html(self.warning_icon)
        self.error_icon_html = pixmap_to_html(self.error_icon)

        error_emitter.errorOccurred.connect(self._on_error_event)
        error_emitter.warningOccurred.connect(self._on_warning_event)

        validation_emitter.errorOccurred.connect(self._on_validation_error)
        validation_emitter.warningOccurred.connect(self._on_validation_warning)

        self._init_ui()

    def set_img_index(self, index):
        self.img_index = index
        self._scale = self._viewer.layers[self.img_index].scale

    def add_error_point(self, coordinate):
        """
        Add a new point to the error points layer.
        Expected coordinate is a 3D tuple (z, x, y).
        """
        self.error_points_layer = self._init_error_points_layer()
        coordinate = upscale_to_3d(coordinate)

        data = self.error_points_layer.data.tolist() if self.error_points_layer.data.size else []
        data.append(coordinate)
        self.error_points_layer.data = np.array(data)

    def add_warning_point(self, coordinate):
        """
            Add a new point to the warning points layer.
            Expected coordinate is a 3D tuple (z, x, y).
            But supports 1D and 2D coordinates as well.
        """
        self.warning_points_layer = self._init_warning_points_layer()
        coordinate = upscale_to_3d(coordinate)
        self.warning_points_layer.add(coordinate)

    def add_warning_points(self, coordinates):
        """
            Add multiple points to the warning points layer.
            Expected coordinates are a list of 3D tuples (z, x, y).
            No support for 1D or 2D coordinates >:(
        """
        self.warning_points_layer = self._init_warning_points_layer()

        self.warning_points_layer.add(coordinates)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.summary_button = RichTextPushButton(self)
        self.summary_button.clicked.connect(self._show_details)
        self.layout().addWidget(self.summary_button)

        self._update_summary()

    def _init_error_points_layer(self):
        layer_name = "Errors"
        if layer_name in self._viewer.layers:
            return self._viewer.layers[layer_name]
        else:
            return self._viewer.add_points(np.empty((0, 3)), name=layer_name, face_color='red', scale=self._scale,
                                           size=6)

    def _init_warning_points_layer(self):
        layer_name = "Filtered beads"
        if layer_name in self._viewer.layers:
            return self._viewer.layers[layer_name]
        else:
            return self._viewer.add_points(np.empty((0, 3)), name=layer_name, face_color='yellow', scale=self._scale,
                                           size=5, opacity=0.5, visible=False)

    def _on_error_event(self, string: str, point: tuple):
        """Add an error message to the display."""
        if string != "":
            self.add_error(string)
        if point:
            self.add_error_point(point)

    def _on_warning_event(self, string: str, points: list[tuple]):
        """Add a warning message to the display."""

        if string != "":
            self.add_warning(string)
        if points:
            self.add_warning_points(points)

    def _on_validation_error(self, string: str, channel: int):
        """ Adds a validation error to the channel errors."""
        if channel not in self.channel_errors:
            self.channel_errors[channel] = []
        self.channel_errors[channel].append(string)
        self._update_summary()

    def _on_validation_warning(self, string: str, channel: int):
        """ Adds a validation warning to the channel warnings."""
        if channel not in self.channel_warnings:
            self.channel_warnings[channel] = []
        self.channel_warnings[channel].append(string)
        self._update_summary()


    def _update_summary(self):
        """Update the button text with a summary of warnings and errors."""
        num_warnings = 0
        num_errors = 0
        for channel in self.channel_warnings:
            num_warnings += len(self.channel_warnings[channel])

        for channel in self.channel_errors:
            num_errors += len(self.channel_errors[channel])

        parts = []
        if num_warnings:
            parts.append(f"{num_warnings} warning{'s' if num_warnings > 1 else ''} {self.warning_icon_html}")
        if num_warnings and num_errors:
            parts.append(" | ")
        if num_errors:
            parts.append(f"{num_errors} error{'s' if num_errors > 1 else ''} {self.error_icon_html}")

        summary_text = f'<div style="display: flex; align-items: center{"; text-decoration: underline" if parts else ""}">{" ".join(parts) if parts else "No issues"}</div>'

        self.summary_button.setText(summary_text)


    def _show_details(self):
        """Show a dialog with detailed error and warning messages."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Issue Details")

        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)

        # TODO: Add this into a debug file
        # print(f"Type: {type(self.summary_button)} | class: {self.summary_button.__class__} | meta_obj: {self.summary_button.metaObject().className()}")
        # print(f"Parent Hierarchy: {self.summary_button.parent()}")
        # print(f"Dynamic Properties:", end="")
        # for prop in self.summary_button.dynamicPropertyNames():
        #     print(prop.data().decode(), self.summary_button.property(prop.data().decode()))

        def add_message(icon, message):
            label = QWidget()
            h_layout = QHBoxLayout(label)
            icon_label = QLabel()

            # Scale the icon to match the height of the text
            scaled_icon = icon.scaledToHeight(30)
            icon_label.setPixmap(scaled_icon)

            text_label = QLabel(message)
            text_label.setAlignment(Qt.AlignLeft)

            h_layout.addWidget(icon_label)
            h_layout.addWidget(text_label)
            h_layout.setAlignment(Qt.AlignLeft)  # Align the layout to the left
            details_layout.addWidget(label)


        for channel in self.channel_warnings:
            for warning in self.channel_warnings[channel]:
                text = f"Warning for {channel}λ: {warning}"
                add_message(self.warning_icon, text)


        for channel in self.channel_errors:
            for error in self.channel_errors[channel]:
                text = f"Error for {channel}λ: {error}"
                add_message(self.error_icon, text)

        if not self.channel_warnings and not self.channel_errors:
            details_layout.addWidget(QLabel("No issues detected."))

        msg_box.layout().addWidget(details_widget)
        msg_box.exec_()

    def add_warning(self, message: str):
        """Add a warning message and update the summary."""
        self.warnings.append(message)
        self._update_summary()

    def add_error(self, message: str):
        """Add an error message and update the summary."""
        self.errors.append(message)
        self._update_summary()

    def clear_channel(self, channel):
        if isinstance(channel, str):
            channel = int(channel)

        if channel in self.channel_errors:
            self.channel_errors[channel].clear()

        if channel in self.channel_warnings:
            self.channel_warnings[channel].clear()

    def clear(self):
        self.warnings = []
        self.errors = []
        self._update_summary()
