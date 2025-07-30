import os

from qmenta import client  # noqa: ignore=E402

SCRIPT = "tool.py"
SETTINGS = "settings.json"
RES_CONF = "results_configuration.json"
DESCRIPTION = "description.html"
local_dockerfile = "Dockerfile"
local_requirements = "requirements.txt"
TEST_TOOL = "test_tool.py"

default_requirements = ["qmenta-sdk-lib"]
src_dir = os.path.join(os.path.dirname(__file__), "templates_tool_maker")


def raise_if_false(evaluation, message):
    if not evaluation:
        raise AssertionError(message)


def build_local_dockerfile() -> None:
    """
    Building the Dockerfile in the local folder to run locally
    """
    # Here we are in the local/ folder, we switch to the test/ folder
    if not os.path.exists(local_dockerfile):
        with open(local_dockerfile, "w") as w1:
            with open(os.path.join(src_dir, "Dockerfile_schema")) as r1:
                w1.write(r1.read())


def build_local_requirements() -> None:
    """
    Preparing the python requirements file in the local folder to run locally

    """
    if not os.path.exists(local_requirements):
        with open(local_requirements, "w") as f1:
            f1.writelines(
                [
                    "# Python requirements for tool:\n",
                    "# Ex: matplotlib==3.4.2\n",
                ]
                + default_requirements
            )


def build_script(code: str) -> None:
    """

    Writing the tool class with the tool_inputs(), run(), and tool_outputs() examples

    Parameters
    ----------
    code: str
        Tool ID provided by the GUI

    """
    with open(os.path.join(src_dir, "tool_schema")) as r1:
        with open(SCRIPT, "w") as w1:
            w1.write(
                r1.read().replace("TOOL_CLASS", convert_to_camel_case(code))
            )


def build_description() -> None:
    """
    Write an empty file, to be filled by the developer
    """
    with open(os.path.join(src_dir, "description_schema")) as r1:
        with open(DESCRIPTION, "w") as w1:
            w1.write(r1.read())


def convert_to_camel_case(code: str) -> str:
    """
    Utils function to convert the ID of the tool to camel case convention string for the class of the tool and the test.

    Parameters
    ----------
    code : str
        Tool ID provided by the GUI

    Returns
    -------
    str
    """
    return "".join([t.capitalize() for t in code.split("_")])


def build_test(code: str, tool_folder: str, version: str) -> None:
    """
    Create internal structure for the local folder, test and sample data

    Parameters
    ----------
    code : str
        Tool ID provided by the GUI
    tool_folder : str
        Tool folder provided by the GUI
    version : str
        Tool version provided by the GUI

    """
    os.makedirs("test/", exist_ok=True)
    os.makedirs("test/sample_data", exist_ok=True)
    os.chdir("test")
    with open(os.path.join(src_dir, "test_tool_schema")) as r1:
        with open(TEST_TOOL, "w") as w1:
            w1.write(
                r1.read()
                .replace("TOOL_CLASS", convert_to_camel_case(code))
                .replace("TOOL_ID", code)
                .replace("TOOL_FOLDER", os.path.join(tool_folder, code))
                .replace("VERSION", version)
            )
