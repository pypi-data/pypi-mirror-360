# -*- coding: utf-8 -*-
# Copyright © kakkarja (K A K)

from tkinter import ttk

__all__ = [""]


class MultipleChoices(ttk.LabelFrame):
    """Multiple Choices"""

    def __init__(self, root, judul: str):
        super().__init__()

        self.config(text=judul)
        self.pack(fill="x")
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(fill="x", expand=1)

        self.lif_left_choice = ttk.LabelFrame(self.left_frame, text="A", labelanchor="w")
        self.lif_left_choice.pack(side="left", fill="x", expand=1)
        self.entry_a = ttk.Entry(self.lif_left_choice)
        self.entry_a.pack(fill="x", expand=1)

        self.lif_mid_choice = ttk.LabelFrame(self.left_frame, text="B", labelanchor="w")
        self.lif_mid_choice.pack(side="left", fill="x", expand=1)
        self.entry_b = ttk.Entry(self.lif_mid_choice)
        self.entry_b.pack(fill="x", expand=1)

        self.lif_right_choice = ttk.LabelFrame(self.left_frame, text="C", labelanchor="w")
        self.lif_right_choice.pack(side="left", fill="x", expand=1)
        self.entry_c = ttk.Entry(self.lif_right_choice)
        self.entry_c.pack(fill="x", expand=1)

    def format_choices(self) -> (dict[str, str] | None):

        entries = [self.entry_a.get().strip(), self.entry_b.get().strip(), self.entry_c.get().strip()]

        if all(entries):
            return {
                "A": entries[0],
                "B": entries[1],
                "C": entries[2],
            }
    
    def delete_all(self):
        entries = [self.entry_a, self.entry_b, self.entry_c]
        for entry in entries:
            entry.delete(0, "end")
        del entries
    
    def insert_text(self, format_: dict[str|str]):
        self.delete_all()
        entries = [self.entry_a, self.entry_b, self.entry_c]
        texts = [format_["A"], format_["B"], format_["C"]]
        for entry, text in zip(entries, texts):
            entry.insert(0, text)
        del entries, text