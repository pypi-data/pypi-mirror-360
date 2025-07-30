from operator import attrgetter
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

import teklia_yolo.extract.utils
from teklia_yolo.extract.bbox import CONFIG_PATH, ElementData, Extractor, SegmZone, Zone


def test_zone():
    zone = Zone(
        class_idx=0,
        polygon="[[58, 3111], [58, 4141], [2695, 4141], [2695, 3111], [58, 3111]]",
        parent_polygon="[[0,0], [3000,0], [3000,5000], [0,5000]]",
    )

    # Check attributes
    assert zone.class_idx == 0
    assert zone.x == 58
    assert zone.y == 3111

    # Check properties
    assert zone.center_x == 1376.5
    assert zone.center_y == 3626

    # Check export
    assert zone.export == "0 0.4588333333333333 0.7252 0.879 0.206"


def test_element_data():
    zones = [
        Zone(
            class_idx=0,
            polygon="[[58, 3111], [58, 4141], [2695, 4141], [2695, 3111], [58, 3111]]",
            parent_polygon="[[0,0], [3000,0], [3000,5000], [0,5000]]",
        )
    ] * 2

    data = ElementData(zones=zones)

    export = data.export().split("\n")
    assert len(export) == 2
    assert export[0] == export[1]
    assert export[0] == "0 0.4588333333333333 0.7252 0.879 0.206"


def test_index_class(mock_database):
    extractor = Extractor(
        zone_class=Zone,
        classes=["text_line"],
        worker_run=None,
        image_format=".jpg",
        image_size=640,
        contrast=False,
    )
    assert extractor.classes == {0: "text_line"}


def test_index_class_error(mock_database):
    with pytest.raises(
        AssertionError, match="All classes are not present in the corpus"
    ):
        Extractor(
            zone_class=Zone,
            classes=["anything"],
            worker_run=None,
            image_format=".jpg",
            image_size=640,
            contrast=False,
        )


@patch.object(teklia_yolo.extract.utils, "download_image")
def test_extract(img_download, mock_database, tmp_path):
    output_path = Path(tmp_path) / "bbox"
    output_path.mkdir()

    # Patch download image to avoid downloading any image
    def simple_image_downloader(url: str, path: str, *args, **kwargs):
        Path(path).touch()

    img_download.side_effect = simple_image_downloader

    Extractor(
        zone_class=Zone,
        classes=["text_line"],
        worker_run=None,
        image_format=".jpg",
        image_size=640,
        contrast=False,
    ).run(
        output=output_path,
        dataset_id="dataset",
        element_type="page",
    )

    # Check YAML config
    assert CONFIG_PATH.exists()
    assert yaml.safe_load(CONFIG_PATH.read_text()) == {
        "path": output_path.name,
        "train": "train.txt",
        "val": "val.txt",
        "test": "test.txt",
        "names": {
            0: "text_line",
        },
    }

    # Cleanup
    CONFIG_PATH.unlink()

    # Check labels config
    assert list(map(attrgetter("name"), sorted(output_path.glob("*.txt")))) == [
        "test.txt",
        "train.txt",
        "val.txt",
    ]

    # Check images count
    images_dir = output_path / "images"

    assert len(list(images_dir.glob("*.jpg"))) == 5

    # Check labels count
    labels_dir = output_path / "labels"

    assert len(list(labels_dir.glob("*.txt"))) == 5

    # Check labels content
    content = (
        # Test page 1
        [
            "0 0.21157894736842106 0.19528371407516582 0.38421052631578945 0.10906411201179071",
            "0 0.20921052631578949 0.29587324981577007 0.38894736842105265 0.09211495946941783",
            "0 0.20921052631578949 0.3971997052321297 0.38894736842105265 0.1105379513633014",
        ],
        # Test page 2
        [
            "0 0.2055263157894737 0.19827586206896552 0.39631578947368423 0.09820089955022489",
            "0 0.2055263157894737 0.3002248875562219 0.39421052631578946 0.10569715142428786",
            "0 0.20605263157894738 0.401424287856072 0.4005263157894737 0.0937031484257871",
        ],
        # Train page 1
        [
            "0 0.2055263157894737 0.1926536731634183 0.38263157894736843 0.10494752623688156",
            "0 0.20605263157894738 0.2972263868065967 0.38263157894736843 0.10269865067466268",
            "0 0.21736842105263157 0.39992503748125935 0.4105263157894737 0.10569715142428786",
            "0 0.21921052631578947 0.5048725637181409 0.4163157894736842 0.10419790104947527",
        ],
        # Train page 2
        [
            "0 0.2023684210526316 0.1942836468885673 0.3857894736842105 0.10347322720694646",
            "0 0.2023684210526316 0.2952243125904486 0.3857894736842105 0.09840810419681621",
            "0 0.2018421052631579 0.3947178002894356 0.3815789473684211 0.10057887120115774",
        ],
        # Val page 1
        [
            "0 0.2023684210526316 0.20043103448275862 0.39 0.09770114942528736",
            "0 0.2005263157894737 0.2995689655172414 0.3863157894736842 0.09626436781609195",
            "0 0.2005263157894737 0.39727011494252873 0.3894736842105263 0.09913793103448276",
        ],
    )
    for filename, expected in zip(
        sorted(list(labels_dir.glob("*.txt")), key=attrgetter("name")),
        content,
        strict=True,
    ):
        assert filename.read_text().split("\n") == expected


@pytest.mark.parametrize(
    (
        "class_idx",
        "polygon",
        "parent_polygon",
        "image_width",
        "image_height",
        "expected_output",
    ),
    [
        (
            0,
            "[[300, 2000], [1500,2000], [1500, 4000], [300, 4000], [300, 2000]]",
            "[[0,0], [1500,0], [1500,4000], [0,4000], [0,0]]",
            3000,
            4000,
            "0 0.2 0.5 1.0 0.5 1.0 1.0 0.2 1.0 0.2 0.5",
        ),
        (
            1,
            "[[1300, 2200], [2500,2200], [2500, 3200], [1300, 3200], [1300, 2200]]",
            "[[1000,1000], [3000,1000], [3000,4000], [1000,4000], [1000,1000]]",
            3000,
            4000,
            "1 0.15 0.4 0.75 0.4 0.75 0.7333333333333333 0.15 0.7333333333333333 0.15 0.4",
        ),
    ],
)
def test_segm_zone(
    class_idx, polygon, parent_polygon, image_width, image_height, expected_output
):
    zone = SegmZone(
        class_idx=class_idx,
        polygon=polygon,
        parent_polygon=parent_polygon,
    )

    assert zone.export == expected_output
