import logging
from pathlib import Path
from uuid import UUID

from arkindex_export import Classification, Dataset, Element, open_database
from peewee import prefetch
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


def add_classification_parser(commands):
    extractor = commands.add_parser(
        "classification", help="Extract dataset for classification task."
    )
    extractor.set_defaults(func=run)

    extractor.add_argument(
        "database", type=Path, help="Path to the Arkindex SQLite export."
    )
    extractor.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to where the dataset will be generated.",
    )
    extractor.add_argument(
        "--dataset-id",
        type=UUID,
        help="ID of the dataset.",
        required=True,
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
        help="Whether to add padding to have squared images of size `--image-size`x`--image-size`.",
    )
    extractor.add_argument(
        "--contrast",
        action="store_true",
        help="Whether to convert image in gray and contrast it.",
    )

    extractor.add_argument(
        "--element-type",
        type=str,
        required=True,
        help="Arkindex element type which holds the classifications.",
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
        help="Specify which classification should be extracted. Extracts all by default.",
    )
    extractor.add_argument(
        "--image-format",
        type=str,
        default=".jpg",
        choices=[".jpg", ".png"],
        help="Format under which images are saved.",
    )


def get_classifications(
    dataset: Dataset,
    set_name: str,
    element_type: str,
    source: str | None,
    class_names: list[str] | None,
):
    """
    List elements under a folder.
    Get their classifications and image url.
    """
    query = get_elements_from_dataset(dataset, set_name).where(
        Element.type == element_type,
    )

    classifications = Classification.select(Classification)
    # Filter on source
    if source == MANUAL:
        classifications = classifications.where(Classification.worker_run.is_null())
    elif source is not None:
        classifications = classifications.where(Classification.worker_run == source)

    # Filter on classification name
    if class_names:
        classifications = classifications.where(
            Classification.class_name.in_(class_names)
        )

    return prefetch(query, classifications)


def process_set(
    output: Path,
    dataset: Dataset,
    set_name: str,
    element_type: str,
    worker_run: str | None,
    image_format: str,
    image_size: int,
    padding: bool,
    contrast: bool,
    class_names: list[str] | None,
) -> list[dict[str, str]]:
    """
    Creates the root folder in output / set_name.
    List elements image/classification and save the image under the corresponding folder.
    """

    data_dir: Path = output / set_name
    data_dir.mkdir(exist_ok=True)

    element_classifications = get_classifications(
        dataset, set_name, element_type, worker_run, class_names
    )

    urls_paths = []

    for element in tqdm(
        element_classifications,
        total=len(element_classifications),
        desc=f"Extracting data from dataset ({dataset.id}) for set ({set_name})",
    ):
        if not element.classification_set:
            continue

        # Take first classification
        classification = element.classification_set[0]

        class_folder = data_dir / classification.class_name
        class_folder.mkdir(exist_ok=True)
        image_path: Path = (class_folder / element.id).with_suffix(image_format)
        if image_path.exists():
            continue

        # Compute image URL
        # IIIF suffix
        url = IIIF_URL.format(
            image_url=element.image.url,
            image_format=image_format,
        )
        # Store image URL and its path
        urls_paths.append(
            {
                "url": url,
                "path": str(image_path),
                "box": get_bbox(element.polygon),
                "resize": [image_size, image_size],
                "padding": padding,
                "contrast": contrast,
            }
        )
    return urls_paths


def run(database: str, output: Path, dataset_id: UUID, *args, **kwargs):
    # Open DB connection
    open_database(database)

    # Create output dir if non existent
    output.mkdir(parents=True, exist_ok=True)

    urls_paths: list[dict[str, str | tuple[int, int]]] = []

    # Retrieve the Dataset and its splits
    dataset, sets = retrieve_dataset_and_sets(dataset_id)

    # Download images
    for set_name in sets:
        urls_paths.extend(process_set(output, dataset, set_name, *args, **kwargs))

    download_images(urls_paths)
