import pytest

from teklia_yolo.extract.utils import get_bbox, preprocess_image
from tests import FIXTURES


def test_preprocess_image_none(tmp_path):
    source = FIXTURES / "427x640.jpg"
    expected_path = FIXTURES / f"{source.stem}-none.jpg"
    output_path = tmp_path / expected_path.name

    preprocess_image(from_path=str(source), to_path=str(output_path))

    assert output_path.read_bytes() == expected_path.read_bytes()


def test_preprocess_image_box(tmp_path):
    source = FIXTURES / "427x640.jpg"
    expected_path = FIXTURES / f"{source.stem}-box.jpg"
    output_path = tmp_path / expected_path.name

    preprocess_image(
        from_path=str(source),
        to_path=str(output_path),
        box=(265, 312, 162, 283),
    )

    assert output_path.read_bytes() == expected_path.read_bytes()


def test_preprocess_image_resize(tmp_path):
    source = FIXTURES / "427x640.jpg"
    expected_path = FIXTURES / f"{source.stem}-resize.jpg"
    output_path = tmp_path / expected_path.name

    preprocess_image(
        from_path=str(source),
        to_path=str(output_path),
        resize=(320, 320),
    )

    assert output_path.read_bytes() == expected_path.read_bytes()


@pytest.mark.parametrize(
    ("thumbnail", "source"),
    [(320, FIXTURES / "427x640.jpg"), (640, FIXTURES / "214x320.jpg")],
)
def test_preprocess_image_padding(thumbnail, source, tmp_path):
    expected_path = FIXTURES / f"{source.stem}-padding.jpg"
    output_path = tmp_path / expected_path.name

    preprocess_image(
        from_path=str(source),
        to_path=str(output_path),
        resize=(thumbnail, thumbnail),
        padding=True,
    )

    assert output_path.read_bytes() == expected_path.read_bytes()


def test_preprocess_image_contrast(tmp_path):
    source = FIXTURES / "427x640.jpg"
    expected_path = FIXTURES / f"{source.stem}-contrast.jpg"
    output_path = tmp_path / expected_path.name

    preprocess_image(
        from_path=str(source),
        to_path=str(output_path),
        contrast=True,
    )

    assert output_path.read_bytes() == expected_path.read_bytes()


@pytest.mark.parametrize(
    ("ark_poly", "iiif_bbox"),
    [
        # Rectangle
        ("[[0, 0], [0, 3453], [2218, 3453], [2218, 0], [0, 0]]", (0, 0, 2218, 3453)),
        # Polygon
        ("[[0, 0], [0, 4000], [2000, 3000], [2000, 0], [0, 0]]", (0, 0, 2000, 4000)),
    ],
)
def test_get_bbox(ark_poly, iiif_bbox):
    assert get_bbox(ark_poly) == iiif_bbox
