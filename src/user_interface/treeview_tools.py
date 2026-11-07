from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import typing
from typing import Callable, Literal, Iterable

def link_treeview_to_scrollbar(tv: ttk.Treeview, sb: ttk.Scrollbar):
    """Connect a treeview to a scrollbar"""
    tv.config(yscrollcommand=sb.set)
    sb.config(command=tv.yview)

def add_double_click_command(treeview: ttk.Treeview, tag: str, command: Callable[[str], None]):
    def action(e: tk.Event):
        row = treeview.identify_row(e.y)
        command(row)
        print(f"{e = }")
        print(f"{treeview.focus() = }")
    bind_str = treeview.tag_bind(tag, "<Double-Button-1>", action)
    def cleanup(e: tk.Event):
        treeview.unbind("<Double-Button-1>", bind_str)
        treeview.unbind("<Destroy>", cleanup_bind_str)
    cleanup_bind_str = treeview.bind("<Destroy>", cleanup, add=True)

class ScrollableTreeview:
    """Bundles a `ttk.Treeview` and a `ttk.Scrollbar` together along with a frame containing them both."""
    frame: ttk.Frame
    treeview: ttk.Treeview
    scrollbar: ttk.Scrollbar

    def __init__(self, master: tk.Misc | None = None, use_row: int = 0, **kwargs) -> None: # pyright: ignore[reportRedeclaration]
        self.frame = ttk.Frame(master)
        self.scrollbar = ttk.Scrollbar(self.frame)
        self.treeview = ttk.Treeview(self.frame, **kwargs)
        link_treeview_to_scrollbar(self.treeview, self.scrollbar)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(use_row, weight=1)
        self.treeview.grid(row=use_row, column=0, sticky="nsew")
        self.scrollbar.grid(row=use_row, column=1, sticky="ns")

        # FYI this is a method
        self.grid = self.frame.grid

    def add_double_click_command(self, tag: str, command: Callable[[str], None]):
        add_double_click_command(self.treeview, tag, command)

    if typing.TYPE_CHECKING: # typing.TYPE_CHECKING is False but the editor/typechecker acts like it's True
        # I made this so my editor will remind me what the parameters of ScrollableTreeview are.
        # The type annotations are copied from ttk.Treeview.__init__ since that's
        # where ScrollableTreeview will send any keyword arguments it receives.
        def __init__(
                self,
                master: tk.Misc | None = None,
                use_row: int = 0,
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

class UpdateCommand(typing.Protocol):
    def __call__(self, query: str, column: str, asc: bool) -> None: pass

class AutoSorter:
    treeview: ttk.Treeview
    sort_asc: bool
    current_column: str
    current_query: str
    update_command: UpdateCommand

    def __init__(self, treeview: ttk.Treeview, update_command: UpdateCommand, initial_query="", initial_asc=True, use_columns: Iterable[str] | None = None) -> None:
        if use_columns is None:
            columns = treeview["columns"]
        else:
            assert type(use_columns) is not str
            columns = tuple(use_columns)
        for column in columns:
            treeview.heading(column, command=self.make_header_command(column))

        self.treeview = treeview
        self.sort_asc = initial_asc
        self.current_column = columns[0]
        self.current_query = initial_query
        self.update_command = update_command

    def refresh(self):
        # TODO: consider persisting the user's selection across refreshes
        self.update_command(self.current_query, self.current_column, self.sort_asc)

    def update_query(self, new_query: str):
        self.current_query = new_query
        self.refresh()

    def make_header_command(self, header: str) -> Callable[[], None]:
        return lambda: self._on_header_click(new_column=header)

    def _on_header_click(self, new_column: str):
        if self.current_column == new_column:
            self.sort_asc = not self.sort_asc
        else:
            self.sort_asc = True
        self.current_column = new_column
        self.refresh()

