# imageToPdf

A Windows application that allows users to combine multiple images into a single PDF file.

## Features

- Combine multiple images into a single PDF document
- Support for various image formats (JPG, PNG, etc.)
- Preview images before conversion
- Reorder images with button click
- Rotate images in the preview
- Simple and intuitive user interface

## Installation

### For Users
Download the latest release executable (.exe) file from the dist folder and run it directly - no installation needed.

### For Developers
1. Clone the repository:
2. install the requirements:
```
pip install -r requirements.txt
```
3. run the app:
```
python main.py
```
Or run the executable file in the dist folder.

To build the executable file, run the following command:
```
pyinstaller --onefile --windowed --icon=icon.ico --name=imageToPdf main.py
```
