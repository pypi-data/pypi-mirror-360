import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from operator import attrgetter
from pathlib import Path
from uuid import UUID

import yaml
from arkindex_export import Dataset, Element, open_database
from arkindex_export.queries import list_children
from more_itertools import flatten
from shapely import Polygon, oriented_envelope
from tqdm import tqdm

from teklia_yolo.extract.utils import (
    IIIF_URL,
    MANUAL,
    download_images,
    get_bbox,
    get_elements_from_dataset,
    retrieve_dataset_and_sets,
    validate_worker_run,
)

logger = logging.getLogger(__name__)
# YOLO default name for this configuration file
CONFIG_PATH = Path("data.yaml")


class YoloTask(Enum):
    Detect = "detect"
    Segment = "segment"
    OBB = "obb"

    def __str__(self) -> str:
        return self.value


@dataclass
class BaseZone:
    class_idx: int
    parent_polygon: str

    def __post_init__(self):
        (
            self.parent_x,
            self.parent_y,
            self.parent_width,
            self.parent_height,
        ) = get_bbox(self.parent_polygon)


@dataclass(init=False)
class Zone(BaseZone):
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    def __init__(self, class_idx: int, polygon: str, parent_polygon: str):
        super().__init__(class_idx, parent_polygon)
        self.x, self.y, self.width, self.height = get_bbox(polygon)
        self.x -= self.parent_x
        self.y -= self.parent_y

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2

    @property
    def export(self) -> str:
        """
        YOLO needs this format
        <class_idx> <center_x> <center_y> <width> <height>

        All coordinates must be normalized by image dimensions
        """
        return " ".join(
            map(
                str,
                [
                    self.class_idx,
                    self.center_x / self.parent_width,
                    self.center_y / self.parent_height,
                    self.width / self.parent_width,
                    self.height / self.parent_height,
                ],
            )
        )


@dataclass
class SegmZone(BaseZone):
    polygon: str

    @property
    def _polygon(self) -> list[tuple[int, int]]:
        return [
            (x - self.parent_x, y - self.parent_y) for x, y in json.loads(self.polygon)
        ]

    @property
    def export(self) -> str:
        """
        YOLO needs this format
        <class_idx> <x1> <y1> <x2> <y2> ... <xn> <yn>

        All coordinates must be normalized by image dimensions
        """
        max_size = max(self.parent_width, self.parent_height)

        # Calculate padding to make the other side equal to `max_size`
        pad_left = max(max_size - self.parent_width, 0) // 2
        pad_top = max(max_size - self.parent_height, 0) // 2

        # Parse polygon
        points = flatten(
            [
                [(x + pad_left) / max_size, (y + pad_top) / max_size]
                for (x, y) in self._polygon
            ]
        )

        return " ".join(
            map(
                str,
                [self.class_idx, *points],
            )
        )


@dataclass
class OBBZone(SegmZone):
    @property
    def _polygon(self) -> list[tuple[int, int]]:
        return list(
            set(
                oriented_envelope(Polygon(super()._polygon)).normalize().exterior.coords
            )
        )


ZONE_CLASS_BY_TASKS = {
    YoloTask.Detect: Zone,
    YoloTask.Segment: SegmZone,
    YoloTask.OBB: OBBZone,
}


@dataclass
class ElementData:
    zones: list[Zone] = field(default_factory=list)

    def export(self) -> str:
        """
        YOLO format is 1 line per detected zone
        """
        return "\n".join(map(attrgetter("export"), self.zones))


def add_detection_parser(commands):
    extractor = commands.add_parser(
        "object", help="Extract dataset for object detection task."
    )
    extractor.set_defaults(func=run)

    extractor.add_argument(
        "task", type=YoloTask, choices=list(YoloTask), help="Task to learn."
    )

    extractor.add_argument(
        "database", type=Path, help="Path to the Arkindex SQLite export."
    )
    extractor.add_argument(
        "--dataset-name",
        type=str,
        required=True,
        help="Name of the dataset. Will be used to create folders.",
    )
    extractor.add_argument(
        "--dataset-id",
        type=UUID,
        help="ID of the dataset.",
        required=True,
    )
    extractor.add_argument(
        "--element-type",
        type=str,
        required=True,
        help="Type of the parent element to extract.",
    )

    extractor.add_argument(
        "--worker-run",
        type=validate_worker_run,
        help=f"Source of the classifications. Use '{MANUAL}' for manual transcriptions.",
    )
    extractor.add_argument(
        "--class",
        type=str,
        nargs="+",
        dest="class_names",
        help="Specify which classifications should be extracted.",
        required=True,
    )
    extractor.add_argument(
        "--image-format",
        type=str,
        default=".jpg",
        choices=[".jpg", ".png"],
        help="Format under which images are saved.",
    )
    extractor.add_argument(
        "--image-size",
        type=int,
        required=False,
        default=640,
        help="Maximum size allowed for the image.",
    )
    extractor.add_argument(
        "--padding",
        action="store_true",
        help="Whether to pad images to have square images.",
    )

    extractor.add_argument(
        "--contrast",
        action="store_true",
        help="Whether to convert image in gray and contrast it.",
    )


class Extractor:
    def __init__(
        self,
        classes: list[str],
        worker_run: str | None,
        image_format: str,
        image_size: int,
        padding: bool,
        contrast: bool,
        zone_class,
    ) -> None:
        self.data: dict[str, dict[str, tuple[str, ElementData]]] = defaultdict(dict)
        self.classes = self.index_classes(classes)
        self.worker_run = worker_run
        self.image_format = image_format
        self.image_size = image_size
        self.padding = padding
        self.contrast = contrast

        self.zone_class = zone_class

    @property
    def worker_run_filter(self):
        if not self.worker_run:
            return
        if self.worker_run == MANUAL:
            return Element.worker_run.is_null()
        return Element.worker_run == self.worker_run

    @cached_property
    def class_names(self):
        return list(self.classes.values())

    def index_classes(self, class_names: list[str]):
        """
        Store classes by index as attribute
        """
        query = Element.select(Element.type).distinct().order_by(Element.type)
        # Look for all element types
        types = [res[0] for res in query.tuples()]
        assert all(
            [name in types for name in class_names]
        ), "All classes are not present in the corpus."
        return {idx: name for idx, name in enumerate(class_names)}

    def get_elements(self, dataset: Dataset, set_name: str, element_type: str):
        return get_elements_from_dataset(dataset, set_name).where(
            Element.type == element_type,
        )

    def process_element(self, element: Element) -> ElementData:
        # Find the zones
        children = list_children(str(element.id)).where(
            Element.type << self.class_names,
        )
        if self.worker_run_filter:
            children = children.where(self.worker_run_filter)

        zones = [
            self.zone_class(
                class_idx=self.class_names.index(child.type),
                polygon=child.polygon,
                parent_polygon=element.polygon,
            )
            for child in children
        ]

        return ElementData(
            zones=zones,
        )

    def process_set(self, dataset: Dataset, element_type: str, set_name: str):
        elements = self.get_elements(dataset, set_name, element_type)
        urls_paths = []

        for element in tqdm(
            elements,
            total=elements.count(),
            desc=f"Extracting data from dataset ({dataset.id}) for set ({set_name})",
        ):
            # Compute ElementData from zones
            self.data[set_name][str(element.id)] = (
                set_name,
                self.process_element(element),
            )

            # Store download URL + path
            image_path: Path = (self.images_dir / element.id).with_suffix(
                self.image_format
            )
            if image_path.exists():
                continue

            # Compute image URL
            # IIIF suffix
            url = IIIF_URL.format(
                image_url=element.image.url,
                image_format=self.image_format,
            )
            # Store image URL and its path
            urls_paths.append(
                {
                    "url": url,
                    "path": str(image_path),
                    "box": get_bbox(element.polygon),
                    "resize": [self.image_size, self.image_size],
                    "padding": self.padding,
                    "contrast": self.contrast,
                }
            )
        return urls_paths

    def export(self):
        """
        - Generate the `data.yaml` with the description of the dataset
        - Save the list of images for each set
        - Save the label of each image
        """
        self.generate_dataset_description()

        for set_data in self.data.values():
            for element_id, (_, data) in set_data.items():
                Path(self.labels_dir / element_id).with_suffix(".txt").write_text(
                    data.export()
                )

    def generate_dataset_description(
        self,
    ) -> None:
        """
        Structure is
        ---
        path: <name/of/dataset> # relative to `datasets` folder
        train: train.txt # where we save the paths of images for training set
        val: val.txt # where we save the paths of images for validation set
        test: test.txt # where we save the paths of images for testing set if present
        names: # Dictionary of class_idx: class_name
        """
        data = {
            "path": self.labels_dir.parent.name,
        }

        for set_name in self.data:
            set_desc = (self.labels_dir.with_name(set_name)).with_suffix(".txt")
            set_desc.write_text(
                "\n".join(
                    str((self.images_dir / element_id).with_suffix(self.image_format))
                    for element_id in self.data[set_name]
                )
            )
            data[set_name] = set_desc.name
        data["names"] = self.classes
        CONFIG_PATH.write_text(
            yaml.safe_dump(data, explicit_start=True, sort_keys=False)
        )
        logger.info("The description of your dataset has been saved at `./data.yaml`")

    def run(
        self,
        output: Path,
        dataset_id: UUID,
        element_type: str,
    ):
        # Create dest dirs
        self.images_dir = output / "images"

        urls_paths: list[dict[str, str]] = []

        # Retrieve the Dataset and its splits
        dataset, sets = retrieve_dataset_and_sets(dataset_id)

        # Download images
        for set_name in sets:
            urls_paths.extend(
                self.process_set(
                    dataset,
                    element_type,
                    set_name=set_name,
                )
            )
        self.images_dir.mkdir(exist_ok=True)
        failed = download_images(urls_paths)

        # Remove failed downloads from data attribute
        for set_name, im_path in failed:
            del self.data[set_name][Path(im_path).stem]

        # Export
        self.labels_dir = self.images_dir.with_name("labels")
        self.labels_dir.mkdir(exist_ok=True)
        self.export()


def run(
    task: YoloTask,
    database: str,
    dataset_name: str,
    dataset_id: UUID,
    element_type: str,
    worker_run: str | None,
    image_format: str,
    class_names: list[str],
    image_size: int,
    padding: bool,
    contrast: bool,
):
    # Open DB connection
    open_database(database)

    # Create output dir if non existent
    datasets_dir = Path("datasets") / dataset_name
    datasets_dir.mkdir(parents=True, exist_ok=True)

    Extractor(
        classes=class_names,
        worker_run=worker_run,
        image_format=image_format,
        image_size=image_size,
        padding=padding,
        contrast=contrast,
        zone_class=ZONE_CLASS_BY_TASKS[task],
    ).run(
        output=datasets_dir,
        dataset_id=dataset_id,
        element_type=element_type,
    )
