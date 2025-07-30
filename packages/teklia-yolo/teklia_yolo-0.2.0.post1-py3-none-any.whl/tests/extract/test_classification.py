import logging
from operator import attrgetter

import pytest

from teklia_yolo.extract.classification import (
    MANUAL,
    Dataset,
    download_images,
    get_classifications,
)


@pytest.mark.parametrize(
    ("set_name", "results", "class_names"),
    [
        # All classes
        ("train", [["A"], ["B"]], []),
        ("val", [["A"], []], []),
        ("test", [["A"], ["B"]], []),
        # Only A class
        ("train", [["A"], []], ["A"]),
    ],
)
@pytest.mark.parametrize("worker_run_id", [MANUAL, "worker_run_id"])
def test_get_classifications(
    mock_database, set_name, results, worker_run_id, class_names
):
    element_classifications = get_classifications(
        dataset=Dataset.select().get(),
        set_name=set_name,
        element_type="page",
        source=worker_run_id,
        class_names=class_names,
    )
    for index, element in enumerate(element_classifications):
        assert (
            list(map(attrgetter("class_name"), element.classification_set))
            == results[index]
        )


def test_download_image_error(caplog, capsys):
    image_url = "git@teklia.com/my-image"
    urls_paths = [{"url": image_url, "path": "/dev/null"}]

    download_images(urls_paths=urls_paths)
    captured = capsys.readouterr()

    # Check error log
    assert len(caplog.record_tuples) == 1
    _, level, msg = caplog.record_tuples[0]
    assert level == logging.ERROR
    assert msg == "Failed to download 1 image(s)."

    # Check stdout
    assert captured.out == "git@teklia.com/my-image: Image URL must be HTTP(S)\n"
