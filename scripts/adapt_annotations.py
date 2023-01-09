import json
import os
import sys

sys.path.append(os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-2]))
from configs.config import SeasyConfig


def correct_annotations(config: SeasyConfig) -> None:
    with open(os.path.join(config.dataset_name, "coco_annotations.json"), "r") as file:
        faulty_annotations = json.load(file)
    faulty_annotations["categories"] = [
        {"id": 1, "supercategory": "coco_annotations", "name": "mms"},
        {"id": 2, "supercategory": "coco_annotations", "name": "mms_nut"},
        {"id": 3, "supercategory": "coco_annotations", "name": "skittle"},
        {"id": 4, "supercategory": "coco_annotations", "name": "bean"},
    ]
    with open(os.path.join(config.dataset_name, "coco_annotations.json"), "w") as file:
        json.dump(faulty_annotations, file)


if __name__ == "__main__":
    configuration = SeasyConfig.load_config()
    correct_annotations(configuration.annotation_correction)
