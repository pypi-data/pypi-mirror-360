import os

from qmenta.sdk.local.context import LocalFile
from .modalities import Modality


class TestFileInput(LocalFile):
    __test__ = False

    def __init__(
        self,
        path: str,
        file_filter_condition_name: str,
        modality: Modality = Modality.none,
        tags=None,
        file_info=None,
        file_name_path: str = "",
        regex: str = ".*",
        mandatory: int = 1,
    ):
        super().__init__(
            os.path.split(path)[0],
            os.path.split(path)[1],
            modality,
            tags,
            file_info,
        )
        if file_info is None:
            file_info = {}
        if tags is None:
            tags = list()
        self.file_name_path = (
            os.path.basename(path) if not file_name_path else file_name_path
        )
        self.path = path
        self.name = path
        self.file_filter_condition_name = file_filter_condition_name
        self.modality = modality.value
        self.tags = tags
        self.file_info = file_info
        self.regex = regex
        self.mandatory = mandatory
