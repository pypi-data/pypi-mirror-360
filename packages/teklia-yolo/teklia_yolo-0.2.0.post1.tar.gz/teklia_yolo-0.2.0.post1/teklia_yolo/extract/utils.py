import json
import logging
import re
from argparse import ArgumentTypeError
from concurrent.futures import Future, ThreadPoolExecutor
from enum import Enum
from io import BytesIO
from operator import attrgetter
from uuid import UUID

import cv2
import requests
from arkindex_export import Dataset, DatasetElement, Element, Image
from PIL import Image as PIL_Image
from PIL import ImageOps
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from tqdm import tqdm

logger = logging.getLogger(__name__)

# See http://docs.python-requests.org/en/master/user/advanced/#timeouts
DOWNLOAD_TIMEOUT = (30, 60)

# replace \t with regular space and consecutive spaces
TRIM_REGEX = re.compile(r"\t?(?: +)")

MANUAL = "manual"
IIIF_URL = "{image_url}/full/full/0/default{image_format}"


def validate_worker_run(value: str) -> str:
    """
    Check that the value is equal to `manual` or is a valid UUID
    """
    if value == MANUAL:
        return value

    try:
        UUID(value)
    except ValueError as e:
        raise ArgumentTypeError(f"Must be either {MANUAL} or a valid UUID") from e

    return value


def _retry_log(retry_state, *args, **kwargs):
    logger.warning(
        f"Request to {retry_state.args[0]} failed ({repr(retry_state.outcome.exception())}), "
        f"retrying in {retry_state.idle_for} seconds"
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2),
    retry=retry_if_exception_type(requests.RequestException),
    before_sleep=_retry_log,
    reraise=True,
)
def _retried_request(url):
    resp = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
    resp.raise_for_status()
    return resp


def add_padding(image: PIL_Image.Image) -> PIL_Image.Image:
    # Get current dimensions
    width, height = image.size

    # Ensure the image is in RGB mode
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Determine the scaling factor to make the longest side equal to `max_size`
    max_size = max(width, height)

    # Calculate padding to make the other side equal to `max_size`
    pad_width = max(max_size - width, 0)
    pad_height = max(max_size - height, 0)

    # Apply padding with the correct fill color (black in this case)
    image = ImageOps.expand(
        image,
        border=(
            pad_width // 2,
            pad_height // 2,
            pad_width - (pad_width // 2),
            pad_height - (pad_height // 2),
        ),
        fill=0,
    )

    assert image.width == image.height, "Image is not squared after padding"

    return image


def preprocess_image(
    from_path: str,
    to_path: str,
    box: tuple[float, float, float, float] | None = None,
    resize: tuple[int, int] | None = None,
    padding: bool = False,
    contrast: bool = False,
) -> None:
    """
    Preprocess a downloaded image:
    1. (OpenCV) convert to gray and add contrast,
    2. (Pillow) crop it to keep the relevant zone,
    3. (Pillow) add padding,
    4. (Pillow) resize it but keep the ratio.
    """
    if contrast:
        image = cv2.cvtColor(cv2.imread(str(from_path)), cv2.COLOR_BGR2GRAY)
        cv2.imwrite(to_path, cv2.equalizeHist(image))

    image = PIL_Image.open(to_path)

    if box:
        x, y, width, height = box
        image = image.crop((x, y, x + width, y + height))

    if resize:
        if padding:
            image = add_padding(image)
        image.thumbnail(resize)

    image.save(to_path)


def download_image(url: str, path: str | None = None, *args, **kwargs) -> None:
    """
    Download an image and save it to given path.
    """
    try:
        assert url.startswith("http"), "Image URL must be HTTP(S)"
        # Download the image
        # Cannot use stream=True as urllib's responses do not support the seek(int) method,
        # which is explicitly required by Image.open on file-like objects
        resp = _retried_request(url)

        PIL_Image.open(BytesIO(resp.content)).save(path)
        # Preprocess the image and prepare it for classification/segmentation
        preprocess_image(path, path, *args, **kwargs)
    except Exception as e:
        raise ImageDownloadError(url=url, exc=e) from e


def download_images(urls_paths: list[dict]) -> list[tuple[str, str]]:
    """
    Download images at the needed path.
    :param urls_paths: List of dictionaries with two keys, `url` gives the download URL, `path` the save location.
    """
    failed_downloads = []
    with (
        tqdm(desc="Downloading images", total=len(urls_paths)) as pbar,
        ThreadPoolExecutor() as executor,
    ):

        def process_future(future: Future):
            """
            Callback function called at the end of the thread
            """
            # Update the progress bar count
            pbar.update(1)
            exc = future.exception()
            if exc is None:
                # No error
                return

            assert isinstance(exc, ImageDownloadError)
            # Save tried URL and error message
            failed_downloads.append((exc.url, exc.message))

        # Submit all tasks
        for task in urls_paths:
            executor.submit(download_image, **task).add_done_callback(process_future)

    if failed_downloads:
        logger.error(f"Failed to download {len(failed_downloads)} image(s).")
        print(*list(map(": ".join, failed_downloads)), sep="\n")

    return failed_downloads


class ImageDownloadError(Exception):
    def __init__(self, url: str, exc: Exception, *args: object) -> None:
        super().__init__(*args)
        self.url = url
        self.message = str(exc)


class Split(Enum):
    Train = "train"
    Val = "val"
    Test = "test"


def get_bbox(polygon: str) -> tuple[int, int, int, int]:
    """
    Arkindex polygon stored as string.
    Returns a list of upper left-most pixel, width and height of the element image.
    """
    poly = json.loads(polygon)
    all_x, all_y = zip(*poly, strict=True)
    x, y = min(all_x), min(all_y)
    width, height = max(all_x) - x, max(all_y) - y
    return int(x), int(y), int(width), int(height)


def retrieve_dataset_and_sets(dataset_id: UUID):
    """
    Retrieve a dataset and its (validated) splits from an SQLite export of an Arkindex corpus.
    """
    dataset = Dataset.get_by_id(dataset_id)

    sets = dataset.sets.split(",")
    assert set(
        sets
    ).issubset(
        set(map(attrgetter("value"), Split))
    ), f'Dataset must have "{Split.Train.value}" and "{Split.Val.value}" steps and may also have a "{Split.Test.value}" step'

    return dataset, sets


def get_elements_from_dataset(dataset: Dataset, split: str):
    """
    Retrieve elements from a specific split in a dataset from an SQLite export of an Arkindex corpus.
    """
    query = (
        Element.select()
        .join(Image)
        .switch(Element)
        .join(DatasetElement)
        .where(
            DatasetElement.dataset == dataset,
            DatasetElement.set_name == split,
        )
    )

    return query
