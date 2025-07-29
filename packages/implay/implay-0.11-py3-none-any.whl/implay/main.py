import numpy as np
from IPython.display import display, Image
import cv2
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual
import threading # For non-blocking animation
import time

# Global variables for controlling playback (specific to this function's instance)
_playing_flag = False
_current_frame_idx = 0
_playback_speed_ms = 50 # Default 50ms per frame

# Store widget references for a specific instance
_output_image_widget = None
_slice_slider_widget = None

def implay(volume_data, axis_to_play=0, image_height=None, image_width=None, normalize=True):
    """
    Creates an interactive player for a 3D NumPy array in a Jupyter Notebook,
    allowing playback along a specified axis. This function mimics MATLAB's implay
    for 3D data by playing slices as an animation.

    Args:
        volume_data (np.ndarray): A 3D NumPy array.
                                  Data type should be convertible to uint8 (e.g., float32, uint16).
        axis_to_play (int, optional): The axis along which to play the slices (0, 1, or 2).
                                      Defaults to 0 (the first dimension).
        image_height (int, optional): Desired height for the displayed image. If None,
                                      the height of the slice will be used. Useful for resizing.
        image_width (int, optional): Desired width for the displayed image. If None,
                                     the width of the slice will be used. Useful for resizing.
        normalize (bool, optional): If True, the image data will be normalized to the 0-255
                                    range and converted to uint8 for display. Set to False
                                    if your data is already in the correct uint8 range.
                                    Defaults to True.
    """
    if volume_data.ndim != 3:
        print("Error: Input volume_data must be a 3D NumPy array.")
        return

    global _playing_flag, _current_frame_idx, _playback_speed_ms
    global _output_image_widget, _slice_slider_widget # For this instance

    _playing_flag = False # Reset for new instance
    _current_frame_idx = 0

    num_slices = volume_data.shape[axis_to_play]
    
    if num_slices == 0:
        print("Error: Volume has no slices to play along the specified axis.")
        return

    # Normalize/Scale and convert to uint8 for display
    if normalize:
        volume_data = np.abs(volume_data)
        if volume_data.dtype != np.uint8 or volume_data.max() > 255 or volume_data.min() < 0:
            if volume_data.max() - volume_data.min() > 0:
                volume_display = (volume_data - volume_data.min()) / \
                                (volume_data.max() - volume_data.min()) * 255
            else: # Handle uniform data
                volume_display = np.full_like(volume_data, 127, dtype=np.float32) # Mid-gray
            volume_display = volume_display.astype(np.uint8)
        else:
            volume_display = volume_data

    # --- Helper function to get and encode a slice ---
    def _get_slice_image_bytes(idx):
        if not (0 <= idx < num_slices):
            return b'' # Return empty bytes if index is out of bounds

        # Extract the slice along the specified axis
        if axis_to_play == 0:
            current_slice = volume_display[idx, :, :]
        elif axis_to_play == 1:
            current_slice = volume_display[:, idx, :]
        elif axis_to_play == 2:
            current_slice = volume_display[:, :, idx]
        else:
            raise ValueError("axis_to_play must be 0, 1, or 2.")

        is_success, buffer = cv2.imencode(".jpeg", current_slice)
        if is_success:
            return buffer.tobytes()
        return b''

    # --- Widget Callbacks ---
    def _on_slider_change(change):
        global _current_frame_idx
        _current_frame_idx = change['new']
        _output_image_widget.value = _get_slice_image_bytes(_current_frame_idx)

    def _play_animation_thread_target():
        global _playing_flag, _current_frame_idx
        while _playing_flag:
            _current_frame_idx = (_current_frame_idx + 1) % num_slices
            _slice_slider_widget.value = _current_frame_idx # This triggers _on_slider_change
            time.sleep(_playback_speed_ms / 1000.0)

    def _on_play_button_clicked(b):
        global _playing_flag
        if not _playing_flag:
            _playing_flag = True
            animation_thread = threading.Thread(target=_play_animation_thread_target)
            animation_thread.daemon = True
            animation_thread.start()

    def _on_pause_button_clicked(b):
        global _playing_flag
        _playing_flag = False

    def _on_speed_slider_change(change):
        global _playback_speed_ms
        _playback_speed_ms = change['new'] * 1000 # Convert seconds to ms

    # --- Create Widgets ---
    _slice_slider_widget = widgets.IntSlider(
        min=0,
        max=num_slices - 1,
        step=1,
        value=0,
        description=f'Slice (Axis {axis_to_play}):',
        continuous_update=False
    )
    _slice_slider_widget.observe(_on_slider_change, names='value')

    play_button = widgets.Button(description="Play")
    pause_button = widgets.Button(description="Pause")
    speed_slider = widgets.FloatSlider(
        min=0.01, max=0.5, step=0.01, value=0.05,
        description='Speed (s/frame):', continuous_update=True
    )
    speed_slider.observe(_on_speed_slider_change, names='value')

    play_button.on_click(_on_play_button_clicked)
    pause_button.on_click(_on_pause_button_clicked)

    # Determine image dimensions for the output widget
    if axis_to_play == 0:
        img_width = volume_data.shape[2]
        img_height = volume_data.shape[1]
    elif axis_to_play == 1:
        img_width = volume_data.shape[2]
        img_height = volume_data.shape[0]
    elif axis_to_play == 2:
        img_width = volume_data.shape[1]
        img_height = volume_data.shape[0]

    _output_image_widget = widgets.Image(
        value=_get_slice_image_bytes(0),
        format='jpeg',
        width=image_width if image_width else img_width*2, # Set width based on slice dimensions
        height=image_height if image_height else img_height*2, # Set height based on slice dimensions
    )

    # Arrange widgets
    controls = widgets.HBox([play_button, pause_button, speed_slider])
    ui = widgets.VBox([controls, _slice_slider_widget, _output_image_widget])

    display(ui)