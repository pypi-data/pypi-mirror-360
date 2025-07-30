#! /usr/bin/env python
import json
import os
import re
from tkinter import filedialog, CENTER, messagebox, END

import ttkbootstrap as ttk
from PIL import Image, ImageTk
from qmenta.core import platform
from qmenta.core.auth import Needs2FAError
from qmenta.sdk.tool_maker.make_files import raise_if_false

FONT = "Consolas"
FONTSIZE = 10

dir_name = ""


def gui_tkinter():
    """
    Creates a graphical user interface (GUI) for publishing workflows to the QMENTA platform.

    This function sets up a Tkinter-based GUI window with the following components:
    1. **Logo and Title**: Displays the QMENTA logo and a title indicating the purpose of the GUI.
    2. **User Credentials Input**: Fields for entering the QMENTA platform username and password.
    3. **Tool Information Input**: Fields for specifying the tool ID, version, and name.
    4. **Folder Selection**: A button to browse and select the folder where the tool is stored.
    5. **Action Buttons**: Buttons to submit the form (pushing the tool to the platform) or quit the application.

    The GUI collects user input, validates it, and returns a dictionary containing the collected data
    when the form is submitted.

    Returns
    -------
    dict
        A dictionary containing the following keys and values:
        - "qmenta_user" (str): The QMENTA platform username to log in.
        - "qmenta_password" (str): The QMENTA platform password to log in.
        - "code" (str): The tool ID.
            Your user ID will be prepended to the code to prevent overwriting existing workflows from other users.
        - "version" (str): The tool version.
        - "folder" (str): The directory path where the tool is stored.
        - "name" (str): The tool name or title.
            It will be the displayed name in the QMENTA Platform when you want to run it.
        - "short_name" (str): A processed version of the tool ID (lowercase, spaces replaced with underscores).

    Notes
    -----
    - The GUI uses the `ttkbootstrap` library for a modern and themed appearance.
    - The `browse_folder` function is called when the "Browse Folder" button is clicked. It updates the
      selected folder path and tool ID based on the folder name.
    - The `submit_form` function is called when the "Push to Platform" button is clicked. It validates
      the input data and closes the GUI if all validations pass.
    - The `quit_tool_creator` function is called when the "Quit" button is clicked. It closes the GUI
      and exits the application.

    Example
    -------
    >>> gui_data = gui_tkinter()
    # User interacts with the GUI:
    # - Enters username: "user123"
    # - Enters password: "password123"
    # - Selects folder: "/path/to/tool_folder"
    # - Enters tool ID: "my_tool"
    # - Enters tool version: "1.0.0"
    # - Enters tool name: "My Tool"
    # Clicks "Push to Platform".
    >>> print(gui_data)
    {
        "qmenta_user": "user123",
        "qmenta_password": "password123",
        "code": "my_tool",
        "version": "1.0.0",
        "folder": "/path/to/tool_folder",
        "name": "My Tool",
        "short_name": "my_tool"
    }
    """

    def browse_folder():
        """
        Handles the action triggered by clicking the "Browse" button to select a workflow folder.

        This method opens a directory dialog for the user to select a folder. Once a folder is selected,
        it performs the following actions:
        1. Sets the selected folder path in the `write_dir` variable.
        2. Updates the `tool_id_entry` field in the GUI with the name of the selected folder.
        3. Checks for a "version" file inside the selected folder. If the file exists, it reads the version
           number and updates the `tool_version_entry` field in the GUI.

        Notes
        -----
        - The `dir_name` variable is updated globally to store the selected folder path.
        - The `write_dir` variable is a `StringVar` GUI component that stores the directory path.
        - The `tool_id_entry` and `tool_version_entry` fields are GUI input fields that display the folder name
          and version, respectively.
        - If the "version" file does not exist in the selected folder, the `tool_version_entry` field remains
          unchanged.

        Example
        -------
        >>> browse_folder()
        # User selects the folder "/path/to/workflow_folder" which contains a "version" file with "1.0.0".
        # After execution:
        # - `dir_name` is set to "/path/to/workflow_folder".
        # - `tool_id_entry` displays "workflow_folder".
        # - `tool_version_entry` displays "1.0.0".
        """
        global dir_name
        dir_name = filedialog.askdirectory()
        write_dir.set(dir_name)
        tool_id_entry.delete(0, END)
        tool_id_entry.insert(0, os.path.basename(dir_name))
        # checking version
        version_file = os.path.join(dir_name, "version")
        if os.path.exists(version_file):
            with open(os.path.join(dir_name, "version")) as fv:
                version = fv.read()
            tool_version_entry.delete(0, END)
            tool_version_entry.insert(0, version)

    def generate_output_object():
        """
        This method collects data entered by the user in various input fields (e.g., user ID, password, tool ID, etc.)
        and organizes them into a structured dictionary. The dictionary can then be used for further processing,
        such as authentication, tool configuration, or saving settings.

        Returns
        -------
        dict
            A dictionary containing the following key-value pairs:
            - "qmenta_user" (str): The user ID to log in in the QMENTA Platform set in the GUI.
            - "qmenta_password" (str): The password to log in in the QMENTA Platform set in the GUI.
            - "code" (str): The tool ID set in the GUI.
            - "version" (str): The version of the tool set in the GUI.
            - "folder" (str): The directory path where outputs or files will be saved, as specified in the GUI.
            - "name" (str): The name of the tool set in the GUI.

        Example
        -------
        >>> result = generate_output_object()
        >>> print(result)
        {
            "qmenta_user": "user123",
            "qmenta_password": "password123",
            "code": "tool_abc",
            "version": "1.0",
            "folder": "/path/to/output",
            "name": "My Tool"
        }

        """
        values = {
            "qmenta_user": user_id_entry.get(),
            "qmenta_password": password_entry.get(),
            "code": tool_id_entry.get(),
            "short_name": tool_id_entry.get(),
            "version": tool_version_entry.get(),
            "folder": write_dir.get(),
            "name": tool_name_entry.get(),
        }
        return values

    def perform_selection_check(values):
        """
        Validates and processes the user input values collected from the GUI.

        This method performs a series of checks on the `values` dictionary to ensure that the input data
        is valid and meets the required criteria. If any validation fails, an error message
        is displayed, and the method returns `False`.

        Parameters
        ----------
        values : dict
            A dictionary containing user input values, typically generated by the `get_user_input_values`
            method. Expected keys include:
            - "code" (str): The tool ID.
            - "folder" (str): The directory path where outputs or files will be saved.
            - "name" (str): The name of the tool.
            - "version" (str): The version of the tool.

        Returns
        -------
        dict or bool
            - If all validations pass, the method returns the processed `values` dictionary with
              additional keys (e.g., "short_name") and modifications (e.g., lowercase tool ID).
            - If any validation fails, an error message is displayed using `messagebox.showerror`,
              and the method returns `False`.

        Raises
        ------
        AssertionError
            If any of the validation checks fail, an `AssertionError` is raised internally, and an
            error message is displayed to the user.

        Notes
        -----
        - The `values` dictionary is modified in place during processing:
            - The "code" (tool ID) must be lowercase and must not contain spaces.
            - The "folder" is validated to ensure it exists and is not empty.
            - The "short_name" key is added, derived from the "code" (tool ID) in lowercase and with
              spaces replaced by underscores.
        - The tool version is validated against a regex pattern to ensure it follows a valid format
          (e.g., "1.0", "2.1.0", "3.0.*").

        Example
        -------
        >>> input_user = {
        ...     "code": "My Tool",
        ...     "folder": "/path/to/folder",
        ...     "name": "My Tool Name",
        ...     "version": "1.p0"
        ... }
        >>> result = perform_selection_check(input_user)
        >>> print(result)
        False

        >>> input_user = {
        ...     "code": "my_tool",
        ...     "folder": "/path/to/folder",
        ...     "name": "My Tool Name",
        ...     "version": "1.0"
        ... }
        >>> result = perform_selection_check(input_user)
        >>> print(result)
        {
            "code": "my_tool",
            "short_name": "my_tool",
            "folder": "/path/to/folder",
            "name": "My Tool Name",
            "version": "1.0"
        }
        """
        try:
            # Validate and process the tool ID
            raise_if_false(
                isinstance(values["code"], str), "Tool ID must be a string."
            )
            raise_if_false(values["code"] != "", "Tool ID must be defined.")
            values["code"] = values["code"].lower()  # Convert to lowercase

            # Validate and process the folder
            raise_if_false(values["folder"] != "", "Folder must be defined.")
            raise_if_false(
                os.path.exists(values["folder"]), "Folder must exist."
            )

            # Ensure tool ID has no spaces and create a short name
            if " " in values["code"]:
                print(
                    "WARNING: Tool code can't have spaces, replacing with under score."
                )
                values["short_name"] = (
                    values["code"].lower().replace(" ", "_")
                )  # Create short name

            # Validate the tool name
            raise_if_false(
                isinstance(values["name"], str), "Tool name must be a string."
            )
            raise_if_false(values["name"] != "", "Tool name must be defined.")

            # Validate the tool version
            raise_if_false(
                values["version"] != "", "Tool version must be defined."
            )
            raise_if_false(
                re.search(r"^(\d+\.)?(\d+\.)?(\*|\d+)$", values["version"]),
                "Version format not valid.",
            )

            return values

        except AssertionError as e:
            messagebox.showerror("Error", f"AN EXCEPTION OCCURRED! {e}")
            return False

    # window
    window = ttk.Window(themename="darkly")
    window.title("Workflow Publishing GUI")

    write_dir = ttk.StringVar()
    # image
    logo = Image.open(
        os.path.join(
            os.path.dirname(__file__), "templates_tool_maker", "qmenta.png"
        )
    ).resize((500, 110))
    img = ImageTk.PhotoImage(logo)
    image_label = ttk.Label(master=window, image=img, padding=5, anchor=CENTER)
    image_label.config(image=img)
    image_label.pack(side="top")

    # title
    title_label = ttk.Label(
        master=window,
        text="Publish you Workflow into the QMENTA Platform. "
        "The workflow should already exist in your local environment.",
    )
    title_label.pack(padx=10, pady=10)

    # title
    title_label = ttk.Label(
        master=window, text="(*) indicates mandatory field."
    )
    title_label.pack(padx=10, pady=10)

    user_id_frame = ttk.Frame(master=window)
    user_id_label = ttk.Label(master=user_id_frame, text="Username*")
    user_id_label.pack(side="left")
    user_id_entry = ttk.Entry(master=user_id_frame)
    user_id_entry.pack(side="left", padx=10)
    user_id_frame.pack(pady=10)

    password_frame = ttk.Frame(master=window)
    password_label = ttk.Label(master=password_frame, text="Password*")
    password_label.pack(side="left")
    password_entry = ttk.Entry(master=password_frame, show="*")
    password_entry.pack(side="left", padx=10)
    password_frame.pack(pady=10)

    # Create a button to browse for a folder
    folder_tool_frame = ttk.Frame(master=window)
    folder_tool_label = ttk.Label(
        master=folder_tool_frame,
        text="Select folder where the tool is stored.*",
    )
    folder_tool_label.pack(side="left")
    folder_tool_button = ttk.Button(
        master=folder_tool_frame, text="Browse Folder", command=browse_folder
    )
    folder_tool_button.pack(side="left", padx=10)
    folder_label = ttk.Label(master=folder_tool_frame, textvariable=write_dir)
    folder_label.pack(side="bottom", pady=10)
    folder_tool_frame.pack(pady=10)

    # input tool ID field
    tool_id_frame = ttk.Frame(master=window)
    tool_id_label = ttk.Label(
        master=tool_id_frame, text="Specify the Workflow ID.*"
    )
    tool_id_label.pack(side="left")
    tool_id_entry = ttk.Entry(master=tool_id_frame)
    tool_id_entry.pack(side="left", padx=10)
    tool_id_frame.pack(pady=10)

    # input tool version field
    tool_version_frame = ttk.Frame(master=window)
    tool_version_label = ttk.Label(
        master=tool_version_frame, text="Specify the tool version.*"
    )
    tool_version_label.pack(side="left")
    tool_version_entry = ttk.Entry(master=tool_version_frame)
    tool_version_entry.pack(side="left", padx=10)
    tool_version_frame.pack(pady=10)

    tool_name_frame = ttk.Frame(master=window)
    tool_name_label = ttk.Label(
        master=tool_name_frame, text="Specify the tool name.*"
    )
    tool_name_label.pack(side="left")
    tool_name_entry = ttk.Entry(master=tool_name_frame)
    tool_name_entry.pack(side="left", padx=10)
    tool_name_frame.pack(pady=10)
    gui_content = {}

    def submit_form():
        gui_content.update(generate_output_object())
        gui_content.update(perform_selection_check(gui_content))
        if gui_content:
            window.destroy()

    action_frame = ttk.Frame(master=window)
    button = ttk.Button(
        master=action_frame,
        text="Publish in QMENTA Platform",
        command=submit_form,
    )
    button.pack(side="left")
    action_frame.pack(pady=10)

    def quit_tool_creator():
        window.destroy()
        print("Closing GUI.")
        exit()

    ttk.Button(
        master=action_frame,
        text="Quit",
        command=quit_tool_creator,
        bootstyle="danger",
    ).pack(side="left", padx=10)

    # run
    window.mainloop()
    return gui_content


def main():
    content_build = gui_tkinter()
    if not content_build:
        exit()
    os.chdir(dir_name)

    user = content_build["qmenta_user"]
    password = content_build["qmenta_password"]
    try:
        auth = platform.Auth.login(
            username=user,
            password=password,
            base_url="https://platform.qmenta.com",
            ask_for_2fa_input=False,
        )
    except Needs2FAError as needs2faerror:
        messagebox.showinfo(
            "Message",
            str(needs2faerror)
            + " Please check the terminal to add the code sent to your phone.",
        )
        auth = platform.Auth.login(
            username=user,
            password=password,
            base_url="https://platform.qmenta.com",
            code_2fa=input("Input 2-FA code:"),
        )

    # Get information from the advanced options file.
    advanced_options = "settings.json"
    raise_if_false(
        os.path.exists(advanced_options),
        "Settings do not exist! Run the local test to create it.",
    )
    with open(advanced_options, "r") as file:
        content_build["advanced_options"] = file.read()

    # Get information from the description file.
    with open("description.html") as fr:
        content_build["description"] = fr.read()

    # Get information from the model file.
    with open("model.flow") as fr:
        content_build["model"] = fr.read()

    content_build["results_configuration"] = {"tools": [], "screen": {}}
    if os.path.exists("results_configuration.json"):
        with open("results_configuration.json", "r") as file:
            results_config = json.load(file)
        # The screen value is expected as a string with escaped chars (dict)
        results_config["screen"] = json.dumps(results_config["screen"])
        content_build["results_configuration"] = json.dumps(
            results_config
        ).replace("{}", "")

    content_build.update(
        {
            "start_condition_code": "output={'OK': True, 'code': 1}",
            "deprecated": "0",
            "average_time": "1",
            "tags": "dev",
        }
    )

    # After creating the workflow, the ID of the workflow must be requested and added to the previous dictionary
    # otherwise it will keep creating new workflows on the platform creating conflicts.
    res = platform.post(
        auth, "a_administrator/upsert_analysis_tool", data=content_build
    )
    if res.json()["success"] == 1:
        print("Tool updated successfully!")
        print(
            "Tool name:",
            content_build["name"],
            "(",
            content_build["code"],
            ":",
            content_build["version"],
            ")",
        )
    else:
        print("ERROR setting the tool.")
        print(res.json())


if __name__ == "__main__":
    main()
