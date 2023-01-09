import os

from typing import Dict, Callable
from yaecs import Configuration


class SeasyConfig(Configuration):
    @staticmethod
    def get_default_config_path() -> str:
        return os.path.join("configs", "config.yaml")

    def append_to_data_path(self, path: str) -> str:
        if not path.startswith(self.data_folder):
            return os.path.join(self.data_folder, path)
        return path

    def make_dataset_path(self, path: str) -> str:
        if not path.startswith(self.data_folder):
            return os.path.join(self.append_to_data_path(self.image_rendering.render_path), path)
        return path

    def parameters_pre_processing(self) -> Dict[str, Callable]:
        return {}

    def parameters_post_processing(self) -> Dict[str, Callable]:
        return {
            "obj_creation.obj_folder": self.append_to_data_path,
            "image_rendering.render_path": self.append_to_data_path,
            "annotation_correction.dataset_name": self.make_dataset_path,
        }
