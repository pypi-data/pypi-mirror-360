import json
from operator import attrgetter
from uuid import uuid4

import pytest
from arkindex_export import (
    Classification,
    Dataset,
    DatasetElement,
    Element,
    ElementPath,
    Image,
    ImageServer,
    WorkerRun,
    WorkerVersion,
    database,
)

from teklia_yolo.extract.utils import Split
from tests import FIXTURES


@pytest.fixture(scope="session")
def mock_database(tmp_path_factory):
    def create_element(id: str, parent: Element | None = None) -> None:
        element_path = (FIXTURES / "extraction" / id).with_suffix(".json")
        element_json = json.loads(element_path.read_text())

        polygon = element_json.get("polygon")

        image_id = id + "-image"
        image, _ = (
            Image.get_or_create(
                id=image_id,
                defaults={
                    "server": image_server,
                    "url": f"http://image/{image_id}/url",
                    "width": 6516,
                    "height": 4690,
                },
            )
            if polygon
            else (None, False)
        )

        element = Element.create(
            id=id,
            name=id,
            type=element_json["type"],
            image=image,
            polygon=json.dumps(polygon) if polygon else None,
            created=0.0,
            updated=0.0,
        )

        if class_name := element_json.get("class_name"):
            # Create classification
            Classification.bulk_create(
                [
                    Classification(
                        id=str(uuid4()),
                        class_name=class_name,
                        element=element,
                        worker_run=worker_run,
                        state="validated",
                        confidence=1,
                        high_confidence=1,
                    )
                    for worker_run in [None, "worker_run_id"]
                ]
            )

        if parent:
            ElementPath.create(id=str(uuid4()), parent=parent, child=element)

        # Recursive function to create children
        for child in element_json.get("children", []):
            create_element(id=child, parent=element)

    MODELS = [
        WorkerVersion,
        WorkerRun,
        ImageServer,
        Image,
        Dataset,
        DatasetElement,
        Element,
        ElementPath,
        Classification,
    ]

    # Initialisation
    tmp_path = tmp_path_factory.mktemp("data")
    database_path = tmp_path / "db.sqlite"
    database.init(
        database_path,
        pragmas={
            # Recommended settings from peewee
            # http://docs.peewee-orm.com/en/latest/peewee/database.html#recommended-settings
            # Do not set journal mode to WAL as it writes in the database
            "cache_size": -1 * 64000,  # 64MB
            "foreign_keys": 1,
            "ignore_check_constraints": 0,
            "synchronous": 0,
        },
    )
    database.connect()

    # Create tables
    database.create_tables(MODELS)

    image_server = ImageServer.create(
        id=0,
        url="http://image/server/url",
        display_name="Image server",
    )

    WorkerRun.create(
        id="worker_run_id",
        worker_version=WorkerVersion.create(
            id="worker_version_id",
            slug="worker_version",
            name="Worker version",
            repository_url="http://repository/url",
            revision="main",
            type="worker",
        ),
    )

    # Create dataset
    splits = list(map(attrgetter("value"), Split))
    dataset = Dataset.create(
        id="dataset",
        name="Dataset",
        description="My dataset",
        state="open",
        sets=",".join(splits),
    )

    # Create dataset elements
    for split in splits:
        element_path = (FIXTURES / "extraction" / split).with_suffix(".json")
        element_json = json.loads(element_path.read_text())

        # Recursive function to create children
        for child in element_json.get("children", []):
            create_element(id=child)

            # Linking the element to the dataset split
            DatasetElement.create(
                id=child, element_id=child, dataset=dataset, set_name=split
            )

    return database_path
