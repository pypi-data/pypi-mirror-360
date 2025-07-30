#! /usr/bin/env python

import json
import os
import re
from tkinter import filedialog, CENTER, END, messagebox

import ttkbootstrap as ttk
from PIL import Image, ImageTk
from qmenta.core import platform
from qmenta.core.auth import Needs2FAError
from qmenta.sdk.tool_maker.make_files import raise_if_false

FONT = "Consolas"
FONTSIZE = 10

MIN = 0
MAX_CORES = 10
MAX_RAM = 16

dir_name = None


def gui_tkinter():
    def browse_folder():
        global dir_name
        dir_name = filedialog.askdirectory()
        write_dir.set(dir_name)
        tool_id_entry.delete(0, END)
        tool_id_entry.insert(0, os.path.basename(dir_name))

        # checking version
        version_file = os.path.join(dir_name, "version")
        with open(version_file) as fv:
            version_ = fv.read()
        tool_version_entry.delete(0, END)
        tool_version_entry.insert(0, version_)
        image_name_entry.delete(0, END)
        image_name_entry.insert(0, os.path.basename(dir_name) + f":{version_}")

    def generate_output_object():
        values = {
            "qmenta_user": user_id_entry.get(),
            "qmenta_password": password_entry.get(),
            "code": tool_id_entry.get(),
            "version": tool_version_entry.get(),
            "name": tool_name_entry.get(),
            "cores": num_cores_entry.get(),
            "memory": memory_entry.get(),
            "image_name": image_name_entry.get(),
            "docker_url": docker_url_entry.get(),
            "docker_user": docker_user_entry.get(),
            "docker_password": tool_version_entry.get(),
        }
        return values

    def perform_selection_check(values):
        try:
            raise_if_false(
                isinstance(values["code"], str), "Tool ID must be a string."
            )
            raise_if_false(values["code"] != "", "Tool ID must be defined.")
            raise_if_false(
                " " not in values["code"], "Tool ID can't have spaces."
            )
            values["code"] = values["code"].lower()  # must be lowercase
            values["short_name"] = (
                values["code"].lower().replace(" ", "_")
            )  # must be lowercase

            raise_if_false(
                isinstance(values["name"], str), "Tool name must be a string."
            )
            raise_if_false(values["name"] != "", "Tool name must be defined.")

            raise_if_false(
                values["version"] != "", "Tool version must be defined."
            )
            raise_if_false(
                re.search(r"^(\d+\.)?(\d+\.)?(\*|\d+)$", values["version"]),
                "Version format not valid.",
            )

            raise_if_false(values["cores"], "Number of cores must be defined.")
            raise_if_false(
                values["cores"].isnumeric(),
                "Number of cores must be an integer.",
            )
            raise_if_false(
                MAX_CORES >= int(values["cores"]) > MIN,
                f"Number of cores must be between {MIN} and {MAX_CORES}.",
            )

            raise_if_false(values["memory"], "RAM must be defined.")
            raise_if_false(
                values["memory"].isnumeric(), "RAM must be an integer."
            )
            raise_if_false(
                MAX_RAM >= int(values["memory"]) > MIN,
                f"RAM must be {MIN} and {MAX_RAM}.",
            )
            values["memory"] = int(values["memory"])
            values["image_name"] = (
                values["image_name"]
                or values["code"] + ":" + values["version"]
            )
            return values
        except AssertionError as e:
            messagebox.showerror("Error", f"AN EXCEPTION OCCURRED! {e}")
            return False

    # window
    window = ttk.Window(themename="darkly")
    window.resizable(False, True)

    window.title("Tool Publishing GUI")
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
        text="QMENTA Platform credentials.",
        font="bold",
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
        master=tool_id_frame, text="Specify the tool ID.*"
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

    num_cores_frame = ttk.Frame(master=window)
    num_cores_label = ttk.Label(
        master=num_cores_frame,
        text="How many cores does the tool require? (integer, "
        f"max. {MAX_CORES})",
    )
    num_cores_label.pack(side="left")
    num_cores_entry = ttk.Entry(master=num_cores_frame)
    num_cores_entry.insert(0, "1")
    num_cores_entry.pack(side="left", padx=10)
    num_cores_frame.pack(pady=10)

    memory_frame = ttk.Frame(master=window)
    memory_label = ttk.Label(
        master=memory_frame,
        text=f"How many GB of RAM does the tool require? "
        f"(integer, max. {MAX_RAM})",
    )
    memory_label.pack(side="left")
    memory_entry = ttk.Entry(master=memory_frame)
    memory_entry.insert(0, "1")
    memory_entry.pack(side="left", padx=10)
    memory_frame.pack(pady=10)

    image_name_frame = ttk.Frame(master=window)
    image_name_label = ttk.Label(
        master=image_name_frame, text="Docker image name"
    )
    image_name_label.pack(side="left")
    image_name_entry = ttk.Entry(master=image_name_frame)
    image_name_entry.pack(side="left", padx=10)
    image_name_frame.pack(pady=10)

    title_label = ttk.Label(
        master=window,
        text="Docker image registry and credentials. "
        "Credentials need to be valid in order to be able to pull the "
        "Docker image from the registry.",
    )
    title_label.pack(padx=10, pady=10)

    docker_url_frame = ttk.Frame(master=window)
    docker_url_label = ttk.Label(
        master=docker_url_frame, text="Docker registry URL"
    )
    docker_url_label.pack(side="left")
    docker_url_entry = ttk.Entry(master=docker_url_frame)
    docker_url_entry.insert(0, "hub.docker.com")
    docker_url_entry.pack(side="left", padx=10)
    docker_url_frame.pack(pady=10)

    docker_user_frame = ttk.Frame(master=window)
    docker_user_label = ttk.Label(
        master=docker_user_frame, text="Docker registry user"
    )
    docker_user_label.pack(side="left")
    docker_user_entry = ttk.Entry(master=docker_user_frame)
    docker_user_entry.pack(side="left", padx=10)
    docker_user_frame.pack(pady=10)

    docker_password_frame = ttk.Frame(master=window)
    docker_password_label = ttk.Label(
        master=docker_password_frame, text="Docker registry password*"
    )
    docker_password_label.pack(side="left")
    docker_password_entry = ttk.Entry(master=docker_password_frame, show="*")
    docker_password_entry.pack(side="left", padx=10)
    docker_password_frame.pack(pady=10)

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
        bootstyle="primary",
    )
    button.pack(side="left")
    action_frame.pack(pady=10)

    def quit_tool_creator():
        window.destroy()
        print("GUI closed.")
        exit()

    ttk.Button(
        action_frame,
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
    with open(advanced_options) as fr:
        content_build["advanced_options"] = fr.read()

    # Get information from the description file.
    with open("description.html") as fr:
        content_build["description"] = fr.read()

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
            "entry_point": "/root/entrypoint.sh",
            "tool_path": "tool:run",
        }
    )

    # After creating the workflow, the ID of the workflow must be requested
    # and added to the previous dictionary
    # otherwise it will keep creating new workflows on the platform
    # creating conflicts.
    res = platform.post(
        auth, "analysis_manager/upsert_user_tool", data=content_build
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
