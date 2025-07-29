## implay: Interactive 3D NumPy Volume Player for Jupyter Notebooks
This project provides a Python function, implay, designed to offer an interactive viewer for 3D NumPy arrays directly within Jupyter Notebook environments. It mimics the functionality of MATLAB's implay by allowing you to "play" through the slices of a 3D volume, providing controls for playback, scrubbing, and optional resizing.
Features
- **Interactive Playback**: Play, pause, and control the speed of the animation through the third dimension (slices) of your NumPy volume.
- **Slice Scrubbing**: A slider allows you to manually navigate through individual slices.
- **Axis Selection**: Choose which axis (dimension) of your 3D array to play as the sequence of slices (axial, coronal, or sagittal views for medical images).
- **Dynamic Resizing**: Optionally resize the displayed slices to a custom height and width.
- **Data Normalization**: Built-in option to normalize your image data to an 8-bit range for optimal display.
- **Jupyter Integration**: Designed to work seamlessly within Jupyter Notebook and JupyterLab.

### Installation
```
pip install implay
```
This project relies on numpy, opencv-python, and ipywidgets.

### Example Usage
Run the following code in a Jupyter cell to see the implay function in action.
* Create a dummy 3D NumPy volume: (depth, height, width)
```
import numpy as np
from implay import implay

num_d, num_h, num_w = 60, 100, 120
test_volume = np.zeros((num_d, num_h, num_w), dtype=np.float32)

implay(test_volume,axis_to_play=0)
```

### Building this version from start
Compiling the code for changes
- `python .\setup.py sdist bdist_wheel`
- `twine check dist/*`