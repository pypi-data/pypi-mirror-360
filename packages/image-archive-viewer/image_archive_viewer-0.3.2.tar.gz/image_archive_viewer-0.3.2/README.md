# Image Archive Viewer

A simple image archive viewer for ZIP, RAR, CBR and CBZ files. Open archive files containing images and browse them in a fullscreen mode with a keyboard- and mouse-friendly user interface.

This archive viewer is built in Python and uses Qt for its user interface. 

It can be used for viewing comic books, photo collections, or any image archives.

## Features

- View images from ZIP, RAR, CBR and CBZ archives (PNG, JPG)
- Fullscreen view
- Mouse and keyboard navigation
- Zoom and pan with mouse or keyboard

The list of files in the archive is sorted alphabetically upon loading.

To see help in the application press "H" at any time.

## Supported Formats

### Archive Formats

- **CBR files** (`.cbr`) - Comic Book RAR files
- **CBZ files** (`.cbz`) - Comic Book ZIP files
- **RAR files** (`.rar`) - RAR archives
- **ZIP files** (`.zip`) - ZIP archives

### Image Formats

- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)

## Installation

### Prerequisites

- Python 3.8 or higher
- unrar (for reading CBR and RAR files)

### Dependencies

- PyQt5
- Pillow
- rarfile (for reading CBR and RAR files)

### Install from PyPI

To install this tool run:

```
pip install image-archive-viewer
```

Using `uv`:

```
uv pip install image-archive-viewer
```

You can also install it as a `uv` tool and then run it directly from shell:

```
uv tool install image-archive-viewer
```

## Usage

After installation, run the viewer:

```bash
show_images
```

You will be prompted to select a ZIP file containing images. The viewer will open in a fullscreen mode.

## Controls

### Navigation
- **Right Arrow** or **Space**: Next image
- **Left Arrow**: Previous image
- **Q** or **Esc**: Quit

### Zoom
- **+** or **=**: Zoom in
- **-**: Zoom out
- **0**: Reset zoom to fit window
- **Mouse wheel**: Zoom in/out (centered on cursor)

### Panning
- **W**: Pan down
- **S**: Pan up
- **A**: Pan right
- **D**: Pan left
- **Mouse drag**: Pan image (when zoomed in)

### Other
- **H**: Show/hide help information 
- **O**: Open a new archive file (ZIP or CBZ)

## Tips

- Press **H** anytime to see a help screen with all available controls
- Use **0** to quickly reset zoom and fit the image to the window
- The mouse wheel zooms centered on your cursor position for precise control
- When zoomed in, you can drag with the mouse to pan around the image

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
