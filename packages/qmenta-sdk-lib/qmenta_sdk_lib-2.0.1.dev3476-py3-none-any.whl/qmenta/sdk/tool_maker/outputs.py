import json
import os
from enum import Enum, unique
from typing import List, Tuple, Union

Option_type = Tuple[object, str]
Options_type = List[Option_type]


@unique
class Coloring(Enum):
    grayscale = "Grayscale"
    custom = "custom"
    custom_random = "custom_random"
    spectrum = "Spectrum"
    overlay_positives = "Overlay (Positives)"
    overlay_negatives = "Overlay (Negatives)"
    hot_n_cold = "Hot-and-Cold"
    gold = "Gold"
    red = "Red Overlay"
    green = "Green Overlay"
    blue = "Blue Overlay"


@unique
class Region(Enum):
    right = "right"
    left = "left"
    center = "center"
    top = "top"
    bottom = "bottom"
    none = ""


@unique
class ToolWidget(Enum):
    # There are more, but I suspect they are no longer supported
    papaya = "papaya"
    html_element = "html_element"
    html_inject = "html_inject"
    action_block = "action_block"


@unique
class LayoutWidget(Enum):
    split = "split"
    tab = "tab"
    tool = "tool"


@unique
class OrientationLayout(Enum):
    vertical = "vertical"
    horizontal = "horizontal"
    none = ""


class ToolScreen:
    def __init__(self, tool_code: ToolWidget, title: str = "", config=None):
        if config is None:
            config = {}
        self.type = "tool"
        self.tool_code = tool_code.value
        self.title = title
        self.config = config


class LayoutScreen:
    def __init__(
        self,
        element_type: LayoutWidget,
        tool: ToolWidget,
        region: Region,
        load_element: int = 0,
        children=None,
        width: str = "",
        height: str = "",
        button_label: str = "",
        orientation: OrientationLayout = OrientationLayout.none,
    ):
        if children is None:
            children = list()
        self.type = element_type.value
        self.tool = tool.value
        self.region = region.value
        self.orientation = orientation.value
        self.children = children
        self.width = width
        self.height = height
        self.button_label = button_label
        self.load_element = load_element


class PapayaViewer:
    def __init__(
        self,
        title,
        width: str = "",
        height: str = "",
        button_label: str = "",
        region: Region = Region.none,
    ):
        self.title = title
        self.region = region
        self.config = {"images": list(), "title": title}
        self.load_element = 0
        self.height = height
        self.width = width
        self.button_label = button_label

    def add_file(self, file: str, coloring: Coloring):
        self.config["images"].append(
            {"file": file, "coloring": coloring.value}
        )

    def get_tool(self):
        return ToolScreen(tool_code=ToolWidget.papaya, config=self.config)

    def get_screen(self):
        return LayoutScreen(
            element_type=LayoutWidget.tool,
            tool=ToolWidget.papaya,
            load_element=self.load_element,
            region=self.region,
            height=self.height,
            width=self.width,
            button_label=self.button_label,
        )

    def __str__(self):
        return f"Papaya load element {self.load_element}"


class HtmlInject:
    def __init__(
        self,
        width: str = "",
        height: str = "",
        button_label: str = "",
        region: Region = Region.none,
    ):
        self.config = {"file": ""}
        self.load_element = 0
        self.height = height
        self.width = width
        self.button_label = button_label
        self.region = region
        self.type = ToolWidget.html_inject
        self.output_files = list()

    def add_html(self, file: str):
        self.config["file"] = file

    def get_tool(self):
        return ToolScreen(tool_code=self.type, config=self.config)

    def get_screen(self):
        return LayoutScreen(
            element_type=LayoutWidget.tool,
            tool=ToolWidget.html_inject,
            load_element=self.load_element,
            region=self.region,
            height=self.height,
            width=self.width,
            button_label=self.button_label,
        )

    def __str__(self):
        return f"Html inject load element {self.load_element}"


class ActionBlockOption:
    def __init__(self, title, value, module: str = ""):
        self.title = title
        self.value = value
        self.module = module


class ActionBlock:
    def __init__(
        self,
        width: str = "",
        height: str = "",
        button_label: str = "",
        question: str = "",
        region: Region = Region.none,
    ):
        self.config = {"options": []}
        self.load_element = 0
        self.height = height
        self.width = width
        self.button_label = button_label
        self.region = region
        self.question = question
        self.type = ToolWidget.action_block

    def add_option(self, option: ActionBlockOption):
        self.config["options"].append(option.__dict__)

    def get_tool(self):
        return ToolScreen(tool_code=self.type, config=self.config)

    def get_screen(self):
        return LayoutScreen(
            element_type=LayoutWidget.tool,
            tool=ToolWidget.html_inject,
            load_element=self.load_element,
            region=self.region,
            height=self.height,
            width=self.width,
            button_label=self.button_label,
        )

    def __str__(self):
        return f"Action block element {self.load_element}"


class HtmlElement:
    def __init__(
        self,
        width: str = "",
        height: str = "",
        button_label: str = "",
        region: Region = Region.none,
    ):
        self.config = {"html": ""}
        self.load_element = 0
        self.height = height
        self.width = width
        self.button_label = button_label
        self.region = region
        self.type = ToolWidget.html_element

    def add_html(self, html_content: str):
        self.config["html"] = html_content

    def get_tool(self):
        return ToolScreen(tool_code=self.type, config=self.config)

    def get_screen(self):
        return LayoutScreen(
            element_type=LayoutWidget.tool,
            tool=ToolWidget.html_element,
            load_element=self.load_element,
            region=self.region,
            height=self.height,
            width=self.width,
            button_label=self.button_label,
        )

    def __str__(self):
        return f"Html element load element {self.load_element}"


class Split:
    def __init__(
        self,
        orientation: OrientationLayout,
        children: List,
        button_label: str = "",
        width: str = "",
        height: str = "",
        region: Region = Region.none,
    ):
        try:
            orientation = orientation.value
        except AttributeError:
            orientation = orientation

        if orientation == OrientationLayout.horizontal.value:
            for element in children:
                try:
                    el_region = element.region.value
                except AttributeError:
                    el_region = element.region
                if el_region != Region.center.value:
                    assert el_region in [
                        Region.top.value,
                        Region.bottom.value,
                    ], f"Region of {element} must be 'top' or 'bottom'."
                assert (
                    element.height != ""
                ), f"'height' of {element} must be defined in {element.__str__()}."

        elif orientation == OrientationLayout.vertical.value:
            for element in children:
                try:
                    el_region = element.region.value
                except AttributeError:
                    el_region = element.region
                if el_region != Region.center.value:
                    assert el_region in [
                        Region.right.value,
                        Region.left.value,
                    ], f"Region of {element} must be 'left' or 'right'."
                assert (
                    element.width != ""
                ), f"'width' of {element} must be defined in {element.__str__()}."
        else:
            raise Exception("Orientation value is not valid.")

        children_list = list()
        for child in children:
            if not isinstance(child, dict):
                children_list.append(process_element(child.get_screen()))
            else:
                children_list.append(child)

        self.children = children_list
        self.orientation = orientation
        self.type = LayoutWidget.split.value
        self.button_label = button_label
        self.height = height
        self.width = width
        self.region = region.value

    def __repr__(self):
        return process_element(self.get_screen())

    def get_screen(self):
        return self

    def get_tool(self):
        return self


class Tab:
    def __init__(
        self,
        children: List,
    ):
        for element in children:
            assert (
                element.button_label != ""
            ), f"'button_label' of {element} must be defined."
        self.type = LayoutWidget.tab.value
        children_list = list()
        for child in children:
            if not isinstance(child, dict):
                children_list.append(process_element(child.get_screen()))
            else:
                children_list.append(child)
        self.children = children_list

    def get_screen(self):
        return self

    def get_tool(self):
        return self

    def __repr__(self):
        return process_element(self.get_screen())


def process_element(new_element):
    return dict((k, v) for k, v in new_element.__dict__.items() if bool(v))


class ResultsConfiguration:
    def __init__(self):
        self.screen = dict()
        self.tools = list()
        self.load_element = 1
        self.elements = dict()

    def add_visualization(
        self,
        new_element: Union[PapayaViewer, HtmlElement, HtmlInject, ActionBlock],
    ):
        new_element.load_element = self.load_element
        tool_dict = process_element(new_element.get_tool())
        self.load_element += 1
        self.tools.append(tool_dict)

    def generate_results_configuration_file(
        self,
        build_screen: Union[List, Tab, Split],
        tool_path: str,
        testing_configuration: bool = False,
    ):
        if isinstance(build_screen, list):
            for new_element in build_screen:
                screen_dict = process_element(new_element.get_screen())
                self.screen.update(screen_dict)
        else:
            self.screen.update(process_element(build_screen.get_screen()))

        output = {"screen": self.screen, "tools": self.tools}
        encoded = json.dumps(output, indent=2)
        if testing_configuration:
            return output
        with open(
            os.path.join(tool_path, "results_configuration.json"), "w"
        ) as f:
            f.write(encoded)
