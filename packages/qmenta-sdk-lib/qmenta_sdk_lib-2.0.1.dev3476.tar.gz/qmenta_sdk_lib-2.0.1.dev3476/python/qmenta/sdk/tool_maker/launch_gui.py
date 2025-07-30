#! /usr/bin/env python

import os
import sys
from tkinter import CENTER, messagebox

import ttkbootstrap as ttk
from PIL import ImageTk, Image
from qmenta.sdk.tool_maker.make_files import (
    build_local_dockerfile,
    build_local_requirements,
    build_script,
    build_test,
    build_description,
    raise_if_false,
)

FONT = "Consolas"
FONTSIZE = 10

MIN = 0
MAX_CORES = 50
MAX_RAM = 150

FOLDER = "local_tools"
sys.path.append(FOLDER)


def gui_tkinter():
    def generate_output_object():
        values = {
            "tool_id": tool_id_entry.get(),
            "tool_version": tool_version_entry.get(),
        }
        return values

    def perform_selection_check(values):
        try:
            raise_if_false(
                isinstance(values["tool_id"], str), "Tool ID must be a string."
            )
            raise_if_false(values["tool_id"] != "", "Tool ID must be defined.")
            raise_if_false(
                " " not in values["tool_id"], "Tool ID can't have spaces."
            )
            values["tool_id"] = values["tool_id"].lower()  # must be lowercase
            values["folder"] = os.getcwd()
            if os.path.exists(
                os.path.join(values["folder"], values["tool_id"])
            ):
                messagebox.showerror(
                    "Python Error", "Error: This is an Error Message!"
                )
            return values
        except AssertionError as e:
            messagebox.showerror("Error", f"AN EXCEPTION OCCURRED! {e}")
            return False

    # window
    window = ttk.Window(themename="darkly")
    window.title("Tool Maker GUI")
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
        text="Fill the fields and click create to automatically generate a new tool file structure.",
        font="bold",
    )
    title_label.pack(padx=10, pady=10)

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
    tool_version_entry.insert(0, "1.0")
    tool_version_entry.pack(side="left", padx=10)
    tool_version_frame.pack(pady=10)

    gui_content = {}

    def submit_form():
        gui_content.update(generate_output_object())
        gui_content.update(perform_selection_check(gui_content))
        if gui_content:
            window.destroy()

    action_frame = ttk.Frame(master=window)
    button = ttk.Button(
        master=action_frame,
        text="Create",
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

    os.makedirs(os.path.join(FOLDER, content_build["tool_id"]), exist_ok=True)
    os.chdir(os.path.join(FOLDER, content_build["tool_id"]))
    build_description()
    build_script(code=content_build["tool_id"])
    with open("version", "w") as f1:
        f1.write(content_build["tool_version"])

    os.makedirs("local", exist_ok=True)
    os.chdir("local")

    build_local_requirements()
    build_local_dockerfile()
    build_test(
        content_build["tool_id"],
        FOLDER,
        content_build["tool_version"],
    )


if __name__ == "__main__":
    main()
