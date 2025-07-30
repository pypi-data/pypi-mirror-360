import logging
import os
from numbers import Number
from types import SimpleNamespace
from typing import List, Tuple

from qmenta.sdk.local.context import LocalAnalysisContext

Option_type = Tuple[object, str]
Options_type = List[Option_type]


def check_options(options, id_):
    assert all(
        [isinstance(o[1], str) for o in options]
    ), f"Title of setting {id_} must by of type 'str'"
    assert len([o[0] for o in options]) == len(
        list(set([o[0] for o in options]))
    ), f"{id_} must unique options."


class Input:
    def __init__(self, id_: str, input_type: str):
        self.id = id_
        self.type = input_type


class CheckBox(Input):
    def __init__(self, id_: str, title: str, default: int = 1):
        super().__init__(id_, "checkbox")
        self.id = id_
        self.title = title
        self.default = default

    def get_input(self, context):
        settings = context.get_settings()
        return bool(settings.get(self.id, self.default))


class String(Input):
    def __init__(self, id_: str, title: str, default: str):
        super().__init__(id_, "string")
        self.id = id_
        self.title = title
        self.default = default

    def get_input(self, context):
        settings = context.get_settings()
        return str(settings.get(self.id, self.default))


class Decimal(Input):
    def __init__(
        self,
        id_: str,
        title: str,
        default: Number,
        _min: Number = -1e9,
        _max: Number = 1e9,
    ):
        super().__init__(id_, "decimal")
        self.id = id_
        self.title = title
        self.default = default
        self.min = _min
        self.max = _max

    def get_input(self, context):
        settings = context.get_settings()
        return float(settings.get(self.id, self.default))


class Integer(Input):
    def __init__(
        self,
        id_: str,
        title: str,
        default: Number,
        _min: Number = 0,
        _max: Number = 1e9,
    ):
        super().__init__(id_, "integer")
        self.id = id_
        self.title = title
        self.default = default
        self.min = _min
        self.max = _max

    def get_input(self, context):
        settings = context.get_settings()
        return int(settings.get(self.id, self.default))


class SingleChoice(Input):
    def __init__(
        self, id_: str, options: Options_type, default: object, title: str
    ):
        super().__init__(id_, "single_choice")
        self.id = id_
        self.title = title
        self.options = options
        self.default = default
        check_options(options, id_)

    def get_input(self, context):
        return context.get_settings().get(self.id, self.default)


class MultipleChoice(Input):
    def __init__(
        self,
        id_: str,
        options: Options_type,
        default: List[object],
        title: str,
    ):
        super().__init__(id_, "multiple_choice")
        self.id = id_
        self.title = title
        self.options = options
        self.default = default
        check_options(options, id_)

    def get_input(self, context):
        return context.get_settings().get(self.id, self.default)


class ContainerHandler(Input):
    def __init__(
        self,
        id_: str,
        file_filter: str,
        title: str = "",
        info: str = "",
        anchor: int = 1,
        batch: int = 1,
        mandatory: int = 1,
        tool_codes_set_as_input=None,
    ):
        super().__init__(id_, "container")

        if tool_codes_set_as_input is None:
            tool_codes_set_as_input = list()
        self.file_filter = file_filter
        self.title = title
        if info:
            self.info = info
        self.in_filter = ["mri_brain_data"]
        self.out_filter = tool_codes_set_as_input
        self.anchor = anchor
        self.batch = batch
        self.mandatory = mandatory

    def get_input(self, context):
        """

        Parameters
        ----------
        context

        Returns
        -------

        """

        logger = logging.getLogger(__name__)
        analysis_dir = os.environ.get("MINTEXE_PATH", "/qmenta")

        # Download files and point to its filename
        fhandlers = SimpleNamespace()

        if isinstance(context, LocalAnalysisContext):
            for k, v in context._LocalAnalysisContext__settings.items():
                if isinstance(v, dict) and "files" in v:
                    context._LocalAnalysisContext__settings[k] = (
                        context._LocalAnalysisContext__settings[k]["files"]
                    )

        filter_names = list()
        for filter_name in self.file_filter.split(
            "["
        ):  # captures the end of file filter name
            filter_names.append(
                filter_name.split(" ")[-1].replace("(", "")
            )  # gets the last string (file filter name)

        for file_filter_condition_name in filter_names[
            :-1
        ]:  # the last element is not the file filter name.
            logger.info(f"Getting files from : {file_filter_condition_name}")
            fhandlers_ = context.get_files(
                self.id, file_filter_condition_name=file_filter_condition_name
            )
            for fh in fhandlers_:
                logger.info(f"Getting handlers from {fh}.")
                logger.info(f"Getting name handler {fh.name}.")
                if "/" in fh.name:
                    folder_to_save_file = ""
                else:
                    folder_to_save_file = os.path.dirname(fh.name)
                if fh.name.endswith(".zip"):
                    folder_to_save_file = os.path.basename(fh.name).replace(
                        ".zip", ""
                    )
                    if "/" in fh.name:
                        folder_to_save_file = fh.name.replace(".zip", "")

                fpath = os.path.join(
                    analysis_dir, "input_folder", self.id, folder_to_save_file
                )

                # This takes into account the path of the file in the input container in the platform
                logger.info(f"Saving to path: {os.path.dirname(fpath)}.")

                # in local testing, we need to create the directory
                os.makedirs(os.path.dirname(fpath), exist_ok=True)

                fh.file_path = fh.download(fpath)

            fhandlers.__setattr__(file_filter_condition_name, fhandlers_)

        return fhandlers


class SubjectHandler(Input):
    def __init__(
        self,
        id_: str,
        file_filter: str,
        title: str = "",
        info: str = "",
        anchor: int = 1,
        batch: int = 1,
        mandatory: int = 1,
        tool_codes_set_as_input=None,
    ):
        super().__init__(id_, "subject")

        if tool_codes_set_as_input is None:
            tool_codes_set_as_input = list()
        self.file_filter = file_filter
        self.title = title
        self.info = info
        self.in_filter = ["mri_brain_data"]
        self.out_filter = tool_codes_set_as_input
        self.anchor = anchor
        self.batch = batch
        self.mandatory = mandatory

    def get_input(self, context):
        pass  # pragma: no cover


class Heading:
    def __init__(self, content: str):
        self.type = "heading"
        self.content = content

    def get_input(self, context):
        pass  # pragma: no cover


class Line:
    def __init__(self):
        self.type = "line"

    def get_input(self, context):
        pass  # pragma: no cover


class IndentText:
    def __init__(self, content: str):
        self.type = "indent"
        self.content = content

    def get_input(self, context):
        pass  # pragma: no cover


class InfoText:
    def __init__(self, content: str):
        self.type = "info"
        self.content = content

    def get_input(self, context):
        pass  # pragma: no cover
