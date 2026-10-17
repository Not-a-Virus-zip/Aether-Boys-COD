from __future__ import annotations
import tkinter as tk
from tkinter import ttk



class TreeviewScroll:
    frame: ttk.Frame
    treeview: ttk.Treeview
    scrollbar: ttk.Scrollbar

    def __init__(self, master: tk.Misc | None = None, **kwargs) -> None:
        self.frame = ttk.Frame(master)
        self.scrollbar = ttk.Scrollbar(self.frame)
        self.treeview = ttk.Treeview(self.frame, yscrollcommand=self.scrollbar.set, **kwargs)
        self.scrollbar.config(command=self.treeview.yview)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.treeview.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)