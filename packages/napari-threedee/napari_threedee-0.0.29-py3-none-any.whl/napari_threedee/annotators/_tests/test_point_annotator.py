from napari.layers import Points

from napari_threedee.annotators.points import PointAnnotator


def test_plane_point_annotator_instantiation(viewer_with_plane_and_points_3d):
    viewer = viewer_with_plane_and_points_3d
    plane_layer = viewer.layers['blobs_3d']
    points_layer = viewer.layers['Points']
    annotator = PointAnnotator(
        viewer=viewer,
        image_layer=plane_layer,
        points_layer=points_layer
    )
    assert isinstance(annotator, PointAnnotator)


def test_plane_point_annotator_auto_creation_of_points_layer(viewer_with_plane_and_points_3d):
    viewer = viewer_with_plane_and_points_3d
    plane_layer = viewer.layers['blobs_3d']
    annotator = PointAnnotator(
        viewer=viewer,
        image_layer=plane_layer,
        points_layer=None
    )
    assert isinstance(annotator.points_layer, Points)
    assert annotator.points_layer.ndim == 3   # matches ndim of image layer