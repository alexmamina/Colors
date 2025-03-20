from tkinter import Frame, Label, Menu, Button, messagebox, Tk
from tkinter import simpledialog
import webbrowser
from typing import Any
from tkmacosx import Button as but
from main import ColorLogic, Board, Coordinates


def create_ui_board(size: int):
    root = Tk()
    board = ColorBoard(root, size)
    board.mainloop()


class ColorBoard(Frame):
    def __init__(self, master: Tk, size: int):
        self.master = self.configure_parent(master)
        super().__init__(self.master)
        self.grid(row=size, column=size)
        self.logic = ColorLogic(size, self)
        self.size = size
        self.button_grid = self.create_button_grid(size, self.logic.color_board.board)

    def configure_parent(self, master) -> Tk:
        master.configure(bg="white")
        window_height = int(0.9 * master.winfo_screenheight())
        screen_width = master.winfo_screenwidth()
        offset = int((screen_width - window_height) / 2)
        master.geometry(f"{window_height}x{window_height}+{offset}+0")
        master.title("Väriaine")
        master.protocol("WM_DELETE_WINDOW", master.destroy)
        return master

    def create_button_grid(self, size: int, colors: list[list[str]]):
        print(colors)
        buttons = []
        for row in range(size):
            buttons.append([])
            for col in range(size):
                b = but(
                    width=75,
                    height=75,
                    border=0,
                    bg="white",
                    borderless=1,
                    # bg=colors[row][col],
                    # command=lambda c=Coordinates(row, col): self.logic.select_and_swap(c)
                )
                b["text"] = colors[row][col],
                b["command"] = (
                    lambda c=Coordinates(row, col): self.logic.select_and_swap(
                        c
                    )
                )
                b["state"] = "normal"
                b.grid(row=row, column=col)
                buttons[row].append(b)
        return buttons

    def select_and_swap_buttons(self, coords: Coordinates):
        print("swapping")
        self.logic.select_and_swap(coords)
        # if self.logic.selected:
        #     self.button_grid[coords.row][coords.col].config(bg="green")
        # else:
        #     self.button_grid[coords.row][coords.col].config(bg="green")
        # self.update_idletasks()

    def highlight_button(self, coords: Coordinates, on: bool = True):
        if on:
            self.button_grid[coords.row][coords.col]["bg"] = "green"
        else:
            self.button_grid[coords.row][coords.col]["bg"] = "white"
        self.update_idletasks()


if __name__ == "__main__":
    create_ui_board(5)
