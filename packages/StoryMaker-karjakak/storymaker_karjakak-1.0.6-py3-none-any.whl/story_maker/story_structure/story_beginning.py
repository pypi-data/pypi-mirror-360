# -*- coding: utf-8 -*-
# Copyright © kakkarja (K A K)

from tkinter import ttk, Text

__all__ = [""]


class BeginningStory(ttk.LabelFrame):
    """Beginning of story"""

    def __init__(self, root):
        super().__init__()
    
        self.config(text="Beginning of a story")
        self.pack(fill="both", expand=1)
        self.frame_top = ttk.Frame(self)
        self.frame_top.pack(fill="both", expand=1)
        self.begin = Text(self.frame_top, height=1, wrap="word")
        self.begin.pack(side="left", fill="both", expand=1)
        self.scrollbar = ttk.Scrollbar(self.frame_top, orient="vertical", command=self.begin.yview)
        self.begin.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

    def format_begin(self) -> (dict[str, str] | None):
        if self.begin.get("1.0", "end")[:-1]:
            return {"begin": self.begin.get("1.0", "end")[:-1].strip()}
        
    def delete_text(self):
        self.begin.delete("1.0", "end")

    def insert_text(self, format_: dict[str|str]):
        self.delete_text()
        self.begin.insert("1.0", format_["begin"])