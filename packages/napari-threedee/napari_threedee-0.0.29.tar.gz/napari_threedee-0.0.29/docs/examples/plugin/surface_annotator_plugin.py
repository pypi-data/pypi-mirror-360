"""
Surface annotator (plugin)
===============================

An example controlling the mesh headlight,
using napari-threedee as a napari plugin.
"""
import napari
from skimage import data

# create napari viewer
viewer = napari.Viewer(ndisplay=3)

# generate image data
blobs = data.binary_blobs(length=64, volume_fraction=0.1, n_dim=3).astype(float)

# add an image layers to the viewer
viewer.add_image(
    blobs,
    name='orange plane',
    rendering='average',
    colormap='bop orange',
    blending='translucent',
    opacity=0.5,
    depiction='plane',
    plane={
    'position': (32, 32, 32),
    'normal': (1, 0, 0),
    'thickness': 10,
    }
)

# add plugin dock widget to viewer
viewer.window.add_plugin_dock_widget(
    plugin_name="napari-threedee", widget_name="surface annotator"
)

# run napari
viewer.layers.selection = [viewer.layers[0]]
viewer.axes.visible = True
viewer.camera.angles = (-15, 25, -30)
viewer.camera.zoom *= 0.5
napari.run()
