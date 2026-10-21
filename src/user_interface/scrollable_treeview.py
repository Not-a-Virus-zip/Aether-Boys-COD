from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import typing
from typing import Callable, Literal

class ScrollableTreeview:
    """Bundles a `ttk.Treeview` and a `ttk.Scrollbar` together along with a frame containing them both."""
    frame: ttk.Frame
    treeview: ttk.Treeview
    scrollbar: ttk.Scrollbar

    def __init__(self, master: tk.Misc | None = None, **kwargs) -> None: # pyright: ignore[reportRedeclaration]
        self.frame = ttk.Frame(master)
        self.scrollbar = ttk.Scrollbar(self.frame)
        self.treeview = ttk.Treeview(self.frame, yscrollcommand=self.scrollbar.set, **kwargs)
        self.scrollbar.config(command=self.treeview.yview)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.treeview.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # FYI this is a method
        self.grid = self.frame.grid

    if typing.TYPE_CHECKING: # typing.TYPE_CHECKING is False but the editor/typechecker acts like it's True
        # I made this so my editor will remind me what the parameters of ScrollableTreeview are.
        # The type annotations are copied from ttk.Treeview.__init__ since that's
        # where ScrollableTreeview will send any keyword arguments it receives.
        def __init__(
                self,
                master: tk.Misc | None = None,
                *,
                class_: str = "",
                columns: str | list[str] | list[int] | list[str | int] | tuple[str | int, ...] = "",
                cursor: str | tuple[str] | tuple[str, str] | tuple[str, str, str] | tuple[str, str, str, str] = "",
                displaycolumns: str | int | list[str] | tuple[str, ...] | list[int] | tuple[int, ...] = ("#all", ),
                height: int = 10, name: str = "...",
                padding: float | str | tuple[float | str] | tuple[float | str, float | str] | tuple[float | str, float | str, float | str] | tuple[float | str, float | str, float | str, float | str] = "...",
                selectmode: Literal['extended'] | Literal['browse'] | Literal['none'] = "extended",
                show: list[str] | tuple[str, ...] | Literal['tree'] | Literal['headings'] | Literal['tree headings'] | Literal[''] = ("tree", "headings"),
                style: str = "", takefocus: bool | Callable[[str], bool | None] | Literal[0] | Literal[1] | Literal[''] = True,
                xscrollcommand: str | Callable[[float, float], object] = "",
                yscrollcommand: str | Callable[[float, float], object] = "") -> None:
            pass