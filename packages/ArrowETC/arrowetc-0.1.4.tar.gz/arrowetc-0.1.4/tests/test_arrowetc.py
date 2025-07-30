import numpy as np
import pytest
from arrowetc import ArrowETC

def test_basic_straight_arrow():
    """Straight arrow with two points and arrowhead should initialize correctly and produce expected geometry."""
    path = [(0, 0), (0, 5)]
    arrow = ArrowETC(path=path, arrow_width=1.0, arrow_head=True)
    
    assert arrow.n_path == 2
    assert arrow.n_segments == 1
    assert arrow.segment_lengths[0] == pytest.approx(5.0)
    assert arrow.vertices.shape[1] == 2
    assert arrow.vertices[0] == pytest.approx((-0.5, 0))
    assert arrow.vertices[3] == pytest.approx((0, 5))
    assert arrow.path_angles[0] == pytest.approx(np.pi / 2)

def test_multi_segmented_arrow():
    """Arrow with multiple segments and bends should compute correct attributes and vertices."""
    path = [(0, 0), (0, 2), (4, -1)]
    arrow = ArrowETC(path=path, arrow_width=1.0, arrow_head=True)

    assert arrow.n_path == 3
    assert arrow.segment_lengths[0] == pytest.approx(2)
    assert arrow.vertices[0] == pytest.approx((-0.5, 0))

    expected_angle = np.arctan2(-3, 4) % (2*np.pi)
    assert arrow.path_angles[1] == pytest.approx(expected_angle)

def test_headless_arrow():
    """Arrow without arrowhead should still produce correct geometry and attributes."""
    path = [(0, 0), (0, 2), (4, -1)]
    arrow = ArrowETC(path=path, arrow_width=1.0, arrow_head=False)

    assert arrow.n_segments == 2
    assert arrow.vertices[0] == pytest.approx((-0.5, 0))

    expected_angle = np.arctan2(-3, 4) % (2*np.pi)
    assert arrow.path_angles[1] == pytest.approx(expected_angle)

def test_bezier_arrow():
    """Arrow constructed with bezier=True should generate curve samples and vertices matching bezier_n."""
    path = [(0, 0), (2, 4), (4, 0)]
    arrow = ArrowETC(path=path, arrow_width=0.5, arrow_head=True, bezier=True, bezier_n=100)

    assert arrow.curve_samples.shape[0] == 100
    assert arrow.vertices.shape[1] == 2

def test_bezier_arrow_no_head():
    """Arrow with bezier=True and arrow_head=False should generate correct curve vertices without head."""
    path = [(0, 0), (2, 4), (4, 0)]
    arrow = ArrowETC(path=path, arrow_width=0.5, arrow_head=False, bezier=True, bezier_n=50)

    # Should have correct number of bezier samples
    assert hasattr(arrow, "curve_samples")
    assert arrow.curve_samples.shape[0] == 50

    # The last curve vertex should be near the last path point - arrow_width/2, since no arrowhead
    last_curve_point = arrow.curve_samples[-1]
    last_vertex = arrow.vertices[len(arrow.curve_samples)-1]
    assert abs(np.linalg.norm(last_curve_point - last_vertex) - 0.5/2) < 0.1

    # Vertices should still wrap around to first point (closing the polygon)
    assert np.allclose(arrow.vertices[0], arrow.vertices[-1], atol=1e-8)

def test_invalid_inputs():
    """Invalid cases like too few points or negative width should raise ValueError."""
    with pytest.raises(ValueError):
        ArrowETC(path=[(0,0)], arrow_width=1.0)
    with pytest.raises(ValueError):
        ArrowETC(path=[(0,0), (1,1)], arrow_width=-1.0)

def test_save_arrow_creates_image(tmp_path):
    """save_arrow() should produce a PNG file."""
    path = [(0, 0), (3, 3)]
    arrow = ArrowETC(path=path, arrow_width=0.5, arrow_head=True)
    out_file = tmp_path / "arrow.png"
    arrow.save_arrow(name=str(out_file))

    assert out_file.exists()
    assert out_file.stat().st_size > 0

def test_get_first_vertex_matches_offset():
    """_get_first_vertex should offset point perpendicularly by half arrow width."""
    path = [(0,0), (1,0)]
    arrow = ArrowETC(path=path, arrow_width=2.0)
    vert = arrow._get_first_vertex(0,0,0)  # horizontal segment → offset should be in +y

    assert vert == pytest.approx((0, 1.0))

def test_vertex_from_angle_parallel_segments():
    """_vertex_from_angle should handle nearly parallel segments producing average normal."""
    path = [(0,0), (1,0), (2,0)]
    arrow = ArrowETC(path=path, arrow_width=1.0)
    vert = arrow._vertex_from_angle(1,0,0,0)

    assert isinstance(vert, np.ndarray)
    assert vert.shape == (2,)

def test_vertex_from_angle_last_segment():
    """_vertex_from_angle should work when theta_2 is None (last segment)."""
    path = [(0,0), (1,0)]
    arrow = ArrowETC(path=path, arrow_width=1.0)
    vert = arrow._vertex_from_angle(1,0,0,None)

    assert isinstance(vert, np.ndarray)

def test_get_arrow_head_vertices_geometry():
    """_get_arrow_head_vertices should produce exactly 5 vertices forming a head."""
    path = [(0,0), (0,1)]
    arrow = ArrowETC(path=path, arrow_width=1.0)
    verts = arrow._get_arrow_head_vertices(0,1,np.pi/2)

    assert len(verts) == 5
    assert all(isinstance(v,np.ndarray) and v.shape==(2,) for v in verts)

def test_get_segment_length_calculates_distances():
    """_get_segment_length should compute expected segment lengths."""
    path = [(0,0), (3,4)]
    arrow = ArrowETC(path=path, arrow_width=0.5)
    lengths = arrow._get_segment_length()

    assert lengths[0] == pytest.approx(5.0)

def test_get_angles_horizontal_and_vertical():
    """_get_angles should return correct angles for horizontal and vertical paths."""
    path = [(0,0), (2,0), (2,3)]
    arrow = ArrowETC(path=path, arrow_width=0.5)
    angles = arrow._get_angles(path)

    assert angles[0] == pytest.approx(0)           # right
    assert angles[1] == pytest.approx(np.pi/2)     # up
