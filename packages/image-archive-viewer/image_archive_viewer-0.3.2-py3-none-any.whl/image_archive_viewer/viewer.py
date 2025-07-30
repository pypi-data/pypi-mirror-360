import sys
import zipfile
import rarfile
import io
import logging
import os
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QLabel, QFileDialog, QWidget, QVBoxLayout
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
import argparse
from typing import Any, Optional, Iterator

logger = logging.getLogger(__name__)

# Setup logging only if enabled by flag
def setup_logging(enable_logging: bool) -> None:
    """
    Set up logging configuration.
    """
    if enable_logging:
        log_format = '[%(levelname)s] %(message)s'
        handlers = [
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('image_archive_viewer.log', mode='w', encoding='utf-8')
        ]
        logging.basicConfig(level=logging.INFO, format=log_format, handlers=handlers)
        logger.setLevel(logging.DEBUG)
        logger.info('Logging enabled (console and file)')
    else:
        logging.basicConfig(level=logging.CRITICAL)  # Only log critical errors
        logger.setLevel(logging.CRITICAL)


def read_images(archive_path: str) -> Iterator[QPixmap]:
    """
    Generator that yields images from a supported archive file.

    Args:
        archive_path (str): Path to the archive file.

    Yields:
        QPixmap: The next image in the archive as a QPixmap.
    """
    
    ext = os.path.splitext(archive_path)[1].lower()
    if ext in ('.zip', '.cbz'):
        archive_opener = zipfile.ZipFile
    elif ext in ('.rar', '.cbr'):
        archive_opener = rarfile.RarFile
    else:
        raise ValueError(f"Unsupported archive type: {archive_path} (extension: {ext})")

    with archive_opener(archive_path, 'r') as archive:
        file_list = sorted(archive.namelist())
        for file_name in file_list:
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                logger.debug(f"Attempting to load: {file_name}")
                try:
                    with archive.open(file_name) as image_file:
                        image_data = image_file.read()
                        logger.debug(f"Read {len(image_data)} bytes from {file_name}")
                        pil_image = Image.open(io.BytesIO(image_data)).convert("RGB")
                        logger.debug(f"PIL image size: {pil_image.size}")
                        bytes_per_line = pil_image.width * 3
                        qimage = QImage(
                            pil_image.tobytes(),
                            pil_image.width,
                            pil_image.height,
                            bytes_per_line,
                            QImage.Format_RGB888
                        )
                        if qimage.isNull():
                            logger.error(f"QImage is null for {file_name}, skipping.")
                            continue
                        pixmap = QPixmap.fromImage(qimage)
                        if pixmap.isNull():
                            logger.error(f"QPixmap is null for {file_name}, skipping.")
                            continue
                        yield pixmap
                        logger.info(f"Successfully loaded: {file_name}")

                except (OSError, ValueError) as e:
                    logger.error(f"Failed to load {file_name}: {e}")
                    logger.debug("Exception info:", exc_info=True)
                    continue


class ArchiveImageSlideshow(QWidget):
    """
    Fullscreen image slideshow widget for viewing images from an archive file.

    Args:
        archive_path (str): Path to the archive file to load images from.
    """

    def __init__(self, archive_path: str) -> None:
        """
        Initialize the slideshow widget and load the archive.

        Args:
            archive_path (str): Path to the archive file.
        """
        super().__init__()

        self.reset_viewer_state()

        self.archive_path = archive_path
        
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(False)

        self.help_label = QLabel(self)
        self.help_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.help_label.setStyleSheet(
            "background-color: rgba(255, 255, 255, 220); color: #222; font-size: 20px; padding: 30px; border-radius: 10px;"
        )
        self.help_label.setVisible(False)
        self.help_label.setWordWrap(True)
        self.help_label.setText(self.get_help_text())
        self.help_label.raise_()

        # Startup overlay
        self.startup_label = QLabel(self)
        self.startup_label.setAlignment(Qt.AlignCenter)
        self.startup_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 200); color: white; font-size: 20px; padding: 40px; border-radius: 15px;"
        )
        self.startup_label.setText("Image Viewer\n\nPress H for help\nPress any other key to continue\n\nPlease wait while images are loaded")
        self.startup_label.raise_()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        self.load_images()

    def reset_viewer_state(self) -> None:
        """
        Reset the viewer state.
        """
        self.images = []
        self.index = 0
        self.zoom_factor = 1.0  # 1.0 means fit to window
        self.pan_offset = [0, 0]  # (x, y) pan offset in pixels
        self.last_mouse_pos = None

    def load_images(self) -> None:
        """
        Load images from the archive file and initialize the viewer.
        """
        self.reset_viewer_state()

        try:
            logger.info(f"Reading archive file: {self.archive_path}")
            reader = read_images(self.archive_path)

            try:
                first_img = next(reader)
                self.images.append(first_img)
            except StopIteration:
                pass

        except rarfile.BadRarFile as e:
            self.startup_label.setText("Error loading RAR/CBR file.\n\nDo you have unrar installed?")
            self.startup_label.raise_()

            # Show startup overlay after window is displayed
            QTimer.singleShot(50, self.show_startup_overlay)

        if not self.images:
            self.label.setText("No PNG or JPG images found in the archive file.")
        else:
            self.show_image()
            QTimer.singleShot(0, self.load_remaining_images)

            # Show startup overlay after window is displayed
            QTimer.singleShot(50, self.show_startup_overlay)


    def load_remaining_images(self) -> None:
        """
        Load the remaining images from the archive.
        """
        reader = read_images(self.archive_path)
        next(reader)  # Skip the first image, already loaded
        for img in reader:
            self.images.append(img)
        # After loading all images, update the startup overlay message
        self.startup_label.setText("Image Viewer\n\nPress H for help\nPress any other key to continue\n\nImages were loaded OK")

    def open_new_file(self) -> None:
        """
        Open a file dialog to select a new archive file and load its images.
        """
        # Prompt user to select a new archive file
        archive_file, _ = QFileDialog.getOpenFileName(
            self, "Select archive file", "", "Archive Files (*.zip *.cbz *.rar *.cbr);;ZIP Files (*.zip);;CBZ Files (*.cbz);;CBR Files (*.cbr);;RAR Files (*.rar)"
        )
        if archive_file:
            self.archive_path = archive_file
            self.load_images()

    def show_image(self) -> None:
        """
        Display the current image, applying zoom and pan as needed.
        """
        if not self.images:
            return
        pixmap = self.images[self.index]
        screen_size = self.size()
        if self.zoom_factor == 1.0:
            # Fit to window
            scaled = pixmap.scaled(
                screen_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.pan_offset = [0, 0]  # Reset pan when fit to window
        else:
            # Zoomed
            width = int(screen_size.width() * self.zoom_factor)
            height = int(screen_size.height() * self.zoom_factor)
            scaled = pixmap.scaled(
                width, height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        # Create a QPixmap the size of the widget and draw the scaled image at the pan offset
        canvas = QPixmap(self.size())
        canvas.fill(Qt.black)
        painter = None
        try:
            from PyQt5.QtGui import QPainter
            painter = QPainter(canvas)
            # Center the image if not panned
            x = (self.width() - scaled.width()) // 2 + self.pan_offset[0]
            y = (self.height() - scaled.height()) // 2 + self.pan_offset[1]
            painter.drawPixmap(x, y, scaled)
        finally:
            if painter:
                painter.end()
        self.label.setPixmap(canvas)

    def next_image(self) -> None:
        """
        Go to the next image in the archive.
        """
        if self.index < len(self.images) - 1:
            self.index += 1
            self.zoom_factor = 1.0
            self.pan_offset = [0, 0]
            self.show_image()

    def previous_image(self) -> None:
        """
        Go back to the previous image in the archive.
        """
        if self.index > 0:
            self.index -= 1
            self.zoom_factor = 1.0
            self.pan_offset = [0, 0]
            self.show_image()

    def keyPressEvent(self, event: Any) -> None:
        """
        Handle key press events.

        Args:
            event: The key event.
        """
        key = event.key()
        
        # Hide startup overlay on any key press
        if self.startup_label.isVisible():
            self.hide_startup_overlay()
            return

        if self.help_label.isVisible() and key != Qt.Key_H:
            self.help_label.setVisible(False)

        if key == Qt.Key_Escape or key == Qt.Key_Q:
            self.close()
        elif key == Qt.Key_Right or key == Qt.Key_Space:
            self.next_image()
        elif key == Qt.Key_Left:
            self.previous_image()
        elif key == Qt.Key_Plus or key == Qt.Key_Equal:
            self.zoom_in()
        elif key == Qt.Key_Minus:
            self.zoom_out()
        elif key == Qt.Key_0:
            self.reset_zoom()
        elif key == Qt.Key_W:
            self.pan_image(0, 50)
        elif key == Qt.Key_S:
            self.pan_image(0, -50)
        elif key == Qt.Key_A:
            self.pan_image(50, 0)
        elif key == Qt.Key_D:
            self.pan_image(-50, 0)
        elif key == Qt.Key_H:
            self.toggle_help_overlay()
        elif key == Qt.Key_O:
            self.open_new_file()

    def zoom_in(self, center: Optional[Any] = None, zoom_rate: float = 1.2) -> None:
        """
        Zoom in on the image.

        Args:
            center: The point to center the zoom on (optional).
            zoom_rate (float): The zoom multiplier.
        """
        old_zoom = self.zoom_factor
        self.zoom_factor *= zoom_rate
        if center:
            self.adjust_pan_for_zoom(center, old_zoom)
        self.show_image()

    def zoom_out(self, center: Optional[Any] = None, zoom_rate: float = 1.2) -> None:
        """
        Zoom out of the image.

        Args:
            center: The point to center the zoom on (optional).
            zoom_rate (float): The zoom divisor.
        """
        old_zoom = self.zoom_factor
        self.zoom_factor /= zoom_rate
        if self.zoom_factor < 0.2:
            self.zoom_factor = 0.2
        if center:
            self.adjust_pan_for_zoom(center, old_zoom)
        self.show_image()

    def reset_zoom(self) -> None:
        """
        Reset zoom to fit the image to the window.
        """
        self.zoom_factor = 1.0
        self.pan_offset = [0, 0]
        self.show_image()

    def adjust_pan_for_zoom(self, center: Any, old_zoom: float) -> None:
        """
        Adjust pan offset so that zooming focuses on the given point.

        Args:
            center: The point to focus zoom on.
            old_zoom (float): The previous zoom factor.
        """
        # Adjust pan so that zooming focuses on the mouse position
        if self.zoom_factor == 1.0:
            self.pan_offset = [0, 0]
            return
        x, y = center.x(), center.y()
        rel_x = x - self.width() / 2 - self.pan_offset[0]
        rel_y = y - self.height() / 2 - self.pan_offset[1]
        scale = self.zoom_factor / old_zoom
        self.pan_offset[0] -= int(rel_x * (scale - 1))
        self.pan_offset[1] -= int(rel_y * (scale - 1))

    def wheelEvent(self, event: Any) -> None:
        """
        Handle mouse wheel events for zooming in and out.

        Args:
            event: The wheel event.
        """
        # Zoom in/out with mouse wheel, centered on cursor
        if event.angleDelta().y() > 0:
            self.zoom_in(center=event.pos(), zoom_rate=1.05)
        else:
            self.zoom_out(center=event.pos(), zoom_rate=1.05)

    def mousePressEvent(self, event: Any) -> None:
        """
        Handle mouse press events.

        Args:
            event: The mouse event.
        """
        if event.button() == Qt.LeftButton:

            # Hide startup overlay on mouse button press
            if self.startup_label.isVisible():
                self.hide_startup_overlay()
                return

            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event: Any) -> None:
        """
        Handle mouse move events for panning the image.

        Args:
            event: The mouse event.
        """
        if self.last_mouse_pos and self.zoom_factor != 1.0:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            self.pan_offset[0] += dx
            self.pan_offset[1] += dy
            self.last_mouse_pos = event.pos()
            self.show_image()

    def mouseReleaseEvent(self, event: Any) -> None:
        """
        Handle mouse release events for ending panning.

        Args:
            event: The mouse event.
        """
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None

    def pan_image(self, dx: int, dy: int) -> None:
        """
        Pan the image by the given x and y offsets.

        Args:
            dx (int): Horizontal pan offset.
            dy (int): Vertical pan offset.
        """
        if self.zoom_factor == 1.0:
            return  # No panning when fit to window
        self.pan_offset[0] += dx
        self.pan_offset[1] += dy
        self.show_image()

    def toggle_help_overlay(self) -> None:
        """
        Show or hide the help overlay.
        """
        if self.help_label.isVisible():
            self.help_label.setVisible(False)
        else:
            self.help_label.setText(self.get_help_text())
            margin = 30
            width = min(500, self.width() - 2 * margin)
            self.help_label.setGeometry(margin, margin, width, self.height() // 2)
            self.help_label.setVisible(True)

        self.help_label.raise_()

    def get_help_text(self) -> str:
        """
        Return the HTML help text for the help overlay.

        Returns:
            str: The help text in HTML format.
        """
        return (
            "<b>Image Viewer Help</b><br><br>"
            "<b>Navigation:</b><br>"
            "Right Arrow / Space: Next image<br>"
            "Left Arrow: Previous image<br>"
            "Q or Esc: Quit<br><br>"
            "<b>Zoom:</b><br>"
            "+ / = : Zoom in<br>"
            "- : Zoom out<br>"
            "0 : Reset zoom<br>"
            "Mouse wheel: Zoom in/out<br><br>"
            "<b>Panning:</b><br>"
            "WASD: Pan image<br>"
            "Mouse drag: Pan image<br><br>"
            "<b>Other:</b><br>"
            "H: Show/hide this help<br>"
            "O: Open a new archive file<br>"
        )

    def resizeEvent(self, event: Any) -> None:
        """
        Handle window resize events to adjust overlays.

        Args:
            event: The resize event.
        """
        super().resizeEvent(event)
        if self.help_label.isVisible():
            margin = 30
            width = min(500, self.width() - 2 * margin)
            self.help_label.setGeometry(margin, margin, width, self.height() // 2)
        # Center the startup overlay
        if self.startup_label.isVisible():
            self.center_startup_overlay()

    def show_startup_overlay(self) -> None:
        """
        Show the startup overlay.
        """
        self.center_startup_overlay()
        self.startup_label.setVisible(True)
        self.startup_label.raise_()

    def center_startup_overlay(self) -> None:
        """
        Center the startup overlay in the window.
        """
        # Center the startup overlay in the window
        label_width = 400
        label_height = 220
        x = (self.width() - label_width) // 2
        y = (self.height() - label_height) // 2
        self.startup_label.setGeometry(x, y, label_width, label_height)

    def hide_startup_overlay(self) -> None:
        """
        Hide the startup overlay.
        """
        self.startup_label.setVisible(False)

    def closeEvent(self, event: Any) -> None:
        """
        Handle the window close event and clear the image cache.

        Args:
            event: The close event.
        """
        logger.info("Shutdown initiated. Clearing image cache...")
        self.images.clear()
        # self.label.setPixmap(QPixmap())  # Clear the currently displayed pixmap
        logger.info("Image cache cleared. Closing.")
        super().closeEvent(event)


def main() -> None:
    """
    Main function of the application. 
    """
    parser = argparse.ArgumentParser(
        description="Image Archive Viewer: view images from ZIP/CBZ/RAR/CBR archives in a fullscreen slideshow.",
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging (console and file)'
    )
    args = parser.parse_args()

    setup_logging(args.verbose)

    app = QApplication(sys.argv)

    # Prompt user to select an archive file
    archive_file, _ = QFileDialog.getOpenFileName(
        None, "Select archive file", "", "Archive Files (*.zip *.cbz *.rar *.cbr);;ZIP Files (*.zip);;CBZ Files (*.cbz);;CBR Files (*.cbr);;RAR Files (*.rar)"
    )
    if not archive_file:
        sys.exit("No file selected.")

    slideshow = ArchiveImageSlideshow(archive_file)
    slideshow.show()
    sys.exit(app.exec_())

