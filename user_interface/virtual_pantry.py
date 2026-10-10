from tkinter import ttk
import tkinter as tk

from . import edit_menu as em
from .. import dummy_business_logic_api as bl

class VirtualPantry:
    name: str = "Virtual Pantry"
    frame: ttk.Frame
    pantry_display: ttk.Treeview
    pantry_contents: list[tuple[bl.Ingredient, bl.Quantity]]
    add_button: ttk.Button
    edit_button: ttk.Button

    def __init__(self, parent: tk.Tk | ttk.Frame, logic: bl.BusinessLogic):
        self.frame = vp_frame = ttk.Frame(parent, name="virtual pantry", padding=20)
        list_frame = ttk.Frame(vp_frame)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.pantry_display = ingr_list = ttk.Treeview(list_frame, columns=["ingr", "qty"], show="headings", selectmode=tk.BROWSE)
        scrollbar = ttk.Scrollbar(list_frame, command=ingr_list.yview)
        ingr_list.config(yscrollcommand=scrollbar.set)
        ingr_list.heading("ingr", text="Ingredient")
        ingr_list.heading("qty", text="Quantity")
        ingr_list.column("ingr", anchor="w")
        ingr_list.column("qty", anchor="e")
        self.pantry_contents = logic.load_virtual_pantry_contents()
        for i, (ingr, quant) in enumerate(self.pantry_contents):
            ingr_list.insert("", "end", id=i, text="", values=[ingr, quant])
        
        scrollbar.grid(row=0, column=1, sticky="ns")
        ingr_list.grid(row=0, column=0, sticky="news")
        list_frame.grid(row=0, column=0, columnspan=2, sticky="news")
        vp_frame.rowconfigure(0, weight=1)
        vp_frame.columnconfigure(0, weight=1)
        vp_frame.columnconfigure(1, weight=1)
        bottom_buttons: list[ttk.Button] = []
        for col, name in enumerate(("Add New", "Edit Selected")):
            button = ttk.Button(vp_frame, text=name)
            button.grid(row=1, column=col, sticky="ew")
            bottom_buttons.append(button)

        self.add_button, self.edit_button = bottom_buttons
        self.add_button.config(command=self.press_add_button)
        self.edit_button.config(command=self.press_edit_button, state=tk.DISABLED)
        ingr_list.bind("<<TreeviewSelect>>", self.on_selection_change)

    def on_selection_change(self, tv: tk.Event) -> object:
        self.edit_button.config(state=tk.NORMAL if self.is_ingr_selected() else tk.DISABLED)
    
    def is_ingr_selected(self) -> bool:
        return len(self.pantry_display.selection()) != 0

    def get_selected(self) -> tuple[bl.Ingredient, bl.Quantity] | None:
        selection = self.pantry_display.selection()
        return None if len(selection) == 0 else self.pantry_contents[int(selection[0])]

    def press_add_button(self):
        print(self.get_selected())

    def press_edit_button(self):
        selection = self.get_selected()
        assert selection is not None, "Edit button should be disabled when nothing is selected"
        name, qty = selection
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Edit Ingredient",
            lambda tl: VPantryEditMenu(tl, name, qty).frame
        )

class VPantryEditMenu(em.EditMenu):
    ingredient_name: em.MenuField[em.Display]
    amount: em.MenuField[em.QuantityEntry]
    save_button: ttk.Button
    cancel_button: ttk.Button

    def __init__(self, container: tk.Toplevel, ingredient_name: str, initial_amount: str) -> None:
        super().__init__(container)
        self.ingredient_name = self.insert("Ingredient", em.Display(self.frame, ingredient_name))
        self.amount          = self.insert("Quantity", em.QuantityEntry(self.frame, initial_amount))
        self.cancel_button, self.save_button = self.finish_construction(["Cancel", 1, "Save Changes"])
