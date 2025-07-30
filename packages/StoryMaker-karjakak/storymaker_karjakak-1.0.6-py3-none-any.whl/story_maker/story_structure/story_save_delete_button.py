# -*- coding: utf-8 -*-
# Copyright © kakkarja (K A K)

from tkinter import ttk
from typing import Any

__all__ = [""]


class SaveDeleteButton(ttk.Frame):
    """Saving Button with 2 commands for Save and Load buttons, with defaults empty"""

    def __init__(self, root, command: dict[str, Any] = {"save": "", "delete": ""}):
        super().__init__()

        self.pack(fill="both")
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(fill="both")
        
        self.save = ttk.Button(self.button_frame,text="Save", command=command["save"],)
        self.save.pack(side="left", ipadx=2, ipady=2, fill="both", expand=1)

        # self.save = ttk.Button(self.button_frame,text="Load", command=command["load"],)
        # self.save.pack(side="left", ipadx=2, ipady=2, fill="both", expand=1)

        self.save = ttk.Button(self.button_frame,text="Delete", command=command["delete"],)
        self.save.pack(side="left", ipadx=2, ipady=2, fill="both", expand=1)