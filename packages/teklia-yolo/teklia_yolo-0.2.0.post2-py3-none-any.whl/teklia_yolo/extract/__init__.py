"""
Extract datasets for training.
"""

from teklia_yolo.extract.bbox import add_detection_parser
from teklia_yolo.extract.classification import add_classification_parser


def add_extract_parser(commands):
    extractor = commands.add_parser(
        "extract", help="Extract a YOLO-compatible dataset."
    )
    subcommands = extractor.add_subparsers()
    add_classification_parser(subcommands)
    add_detection_parser(subcommands)
