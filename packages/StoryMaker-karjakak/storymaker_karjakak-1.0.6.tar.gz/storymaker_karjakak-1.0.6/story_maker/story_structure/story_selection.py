# -*- coding: utf-8 -*-
# Copyright © kakkarja (K A K)

from tkinter import ttk
from pathlib import Path
from typing import Any


class StorySelection(ttk.Frame):

    def __init__(self, root, path: Path):
        super().__init__()
        self.path = path

        self.pack(fill="both")
        self.combo_frame = ttk.Frame(self)
        self.combo_frame.pack(fill="both")

        self.combo_stories = ttk.Combobox(self.combo_frame, width = 30)
        self.combo_stories.pack(side="top", pady=1)
        self.combo_stories.bind("<<ComboboxSelected>>", self.combo_select)
        self.combo_stories["value"] = [
            directory.name for directory in self.path.iterdir() if directory.is_dir()
        ]
        self.style = ttk.Style()
        self.style.configure('my.TButton', font=('Helvetica', 20, "bold"), width=1)
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack()
        self.back_button = ttk.Button(self.button_frame, text="<", style="my.TButton", command=self.previous_folder)
        self.back_button.pack(side="left", padx=(0, 2))
        self.fwd_button = ttk.Button(self.button_frame, text=">", style="my.TButton", command=self.selected_folder)
        self.fwd_button.pack(side="left")
        self.folder = None

    def _reload_combo(self, folder: Path, file: bool = True):
        self.combo_stories.delete(0, "end")
        val = [
            file.name[:-4] for file in folder.iterdir() if ".zip" in file.name
        ] if file else [
            directory.name for directory in folder.iterdir() if directory.is_dir()
        ]
        self.combo_stories["value"] = val
        self.path = folder
        
    def _read_only(self, read: bool = True):
        if read:
            self.combo_stories.config(state="readonly")
        else:
            self.combo_stories.config(state="normal")

    def combo_select(self, event=None):
        if folder := self.combo_stories.get():
            if self.path.joinpath(folder).is_dir():
                self._reload_combo(self.path.joinpath(folder))
                self._read_only()
                self.folder = folder
                del folder

    def previous_folder(self):
        if self.folder:
            if self.path.name == self.folder:
                self._read_only(False)
                self._reload_combo(self.path.parent, False)
    
    def selected_folder(self):
        if self.folder:
            if self.path.joinpath(self.folder).is_dir():
                self._reload_combo(self.path.joinpath(self.folder))
                self._read_only()
    
    def checking_dir(self):
        if self.path.name == "StoryMaker":
            return True
        return False
    
    def _state_combo_read(self):
        if str(self.combo_stories.cget("state")) == "readonly":
            return True
        return False
    
    def reload(self):
        if self.checking_dir():
            if self._state_combo_read():
                self._read_only(False)
            self._reload_combo(self.path, False)
        else:
            if self._state_combo_read():
                self._read_only(False)
            self._reload_combo(self.path)
            self._read_only()
    
    def combo_values(self):
        return bool(self.combo_stories["value"])
    
    def del_folder(self):
        if self.folder and self.path.name == self.folder:
            if not self.combo_values():
                self.path.rmdir()
                self.path = self.path.parent
