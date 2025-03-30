import PyQt6.QtCore as qcore
import PyQt6.QtWidgets as qwidget
import PyQt6.QtGui as qgui
import sys
from functools import partial
from typing import Optional, Callable
from math import floor
from random import randint
import os

from main import ColorLogic, Coordinates, PinnedPoints

DEFAULT_WINDOW_SIZE = 500
RED = "#ff0000"
GREEN = "#22ff00"


class ColorButton(qwidget.QPushButton):
    def __init__(self, color: str, window_height: int, btn_row_size: int):
        super(ColorButton, self).__init__()
        button_height = floor(window_height / btn_row_size)
        self.setAutoFillBackground(True)
        self.setMinimumSize(qcore.QSize(button_height, button_height))
        # Allow resizing buttons
        policy = qwidget.QSizePolicy.Policy.Minimum
        self.setSizePolicy(qwidget.QSizePolicy(policy, policy))
        self.fg = "black"
        self.set_color(color)

    def set_color(self, color: str):
        self.bg = color
        self.set_border(color)
        self.update_style()

    def set_border(self, border: str):
        self.border = f"2px solid {border}"
        self.update_style()

    def update_style(self):
        style = f"{{background-color: {self.bg}; color: {self.fg}"
        if self.border:
            style += f"; border: {self.border};}}"
        else:
            style += ";}"
        self.setStyleSheet(f"QPushButton {style}")

    def disable(self):
        font = self.font()
        font.setPointSize(50)
        self.setFont(font)
        self.setText(".")
        self.setEnabled(False)

    # def mouseMoveEvent(self, e):
    #     if e.buttons() == Qt.MouseButton.LeftButton:
    #         drag = QDrag(self)
    #         mime = QMimeData()
    #         drag.setMimeData(mime)

    #         pixmap = QPixmap(self.size())
    #         self.render(pixmap)
    #         drag.setPixmap(pixmap)

    #         drag.exec(Qt.DropAction.MoveAction)


class AskSize(qwidget.QDialog):
    def __init__(self, parent: "QBoard"):
        super().__init__(parent)

        self.setWindowTitle("New game!")

        message = qwidget.QLabel("Enter the size of the board (length, 3-10), then press Enter")

        self.input_number = qwidget.QLineEdit(self)
        self.input_number.setMaxLength(10)
        self.input_number.returnPressed.connect(self.save_text)
        # Only ints, at most 2 digits
        self.input_number.setInputMask('00')

        layout = qwidget.QVBoxLayout()
        layout.addWidget(message)
        layout.addWidget(self.input_number)
        self.setLayout(layout)

    def save_text(self):
        parent = self.parent()
        # This is always true but saying for the editor
        if parent and isinstance(parent, QBoard):
            parent.new_game_size = int(self.input_number.text())
        self.close()


class QBoard(qwidget.QMainWindow):

    def __init__(self, size: int, window_height: int, center) -> None:
        super().__init__()
        self.setWindowTitle("Väriaine")
        self.new_game_size = 0
        self.setAcceptDrops(True)
        self.window_height = window_height
        self.center = center
        self.logic = ColorLogic(size, self)
        self.pinned_points = PinnedPoints(size)
        self.button_grid, self.button_holder = self.create_button_grid(size)
        self.setCentralWidget(self.button_holder)
        shape = self.frameGeometry()
        shape.moveCenter(center)
        self.move(shape.topLeft())
        self.setup_toolbar()
        self.setMinimumSize(self.sizeHint())

    # def dragEnterEvent(self, e):
    #     e.accept()

    # def dropEvent(self, e):
    #     pos = e.position()
    #     widget = e.source()
    #     self.button_holder.removeWidget(widget)

    #     for n in range(self.button_holder.count()):
    #         # Get the widget at each index in turn.
    #         w = self.button_holder.itemAt(n).widget()
    #         if pos.x() < w.x() + w.size().width() // 2:
    #             # We didn't drag past this widget.
    #             # insert to the left of it.
    #             break
    #     else:
    #         # We aren't on the left hand side of any widget,
    #         # so we're at the end. Increment 1 to insert after.
    #         n += 1

    #     self.blayout.insertWidget(n, widget)
    #     e.accept()

    def setup_toolbar(self):
        toolbar = qwidget.QToolBar("Tools")
        self.addToolBar(toolbar)

        self.add_toolbar_action(
            toolbar,
            "Save color palette",
            "Save color palette as image",
            self.save_image_palette,
        )

        self.add_toolbar_action(
            toolbar,
            "Save color hex codes",
            "Save color palette as a list of hex codes",
            self.save_colors_hex,
        )

        self.add_toolbar_action(
            toolbar,
            "Hint",
            "Show a hint where one color should go (red -> green)",
            self.show_hint,
        )

        self.add_toolbar_action(toolbar, "Hide hints", "Hide any shown hints", self.reset_hint)

        self.add_toolbar_action(
            toolbar,
            "Start new board",
            "Leave this palette and start a new game",
            self.start_new,
        )

    def add_toolbar_action(self, bar: qwidget.QToolBar, title: str, hint: str, function: Callable):
        tool_button = qgui.QAction(title, self)
        tool_button.setToolTip(hint)
        tool_button.triggered.connect(function)
        bar.addAction(tool_button)
        bar.addSeparator()

    def create_button_grid(self, size: int) -> tuple[list[list[ColorButton]], qwidget.QWidget]:
        buttons = []
        layout = qwidget.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        for row in range(size):
            buttons.append([])
            for col in range(size):
                coords = Coordinates(row, col)
                color = self.logic.color_board.get_cell(coords)
                color_button = ColorButton(color, self.window_height, size)
                if not self.pinned_points.has(coords):
                    color_button.setCheckable(True)
                    color_button.clicked.connect(partial(self.logic.select_and_swap, coords))
                else:
                    color_button.disable()
                layout.addWidget(color_button, row, col)
                buttons[row].append(color_button)

        button_holder = qwidget.QWidget()
        button_holder.setLayout(layout)

        return buttons, button_holder

    def highlight_button(self, coords: Coordinates, color: str):
        self.button_grid[coords.row][coords.col].set_color(color)
        self.button_grid[coords.row][coords.col].setChecked(False)

    def show_win(self, moves: Optional[int]):
        win_msg = "You win!\n"
        if moves:
            win_msg += f"Total moves taken: {moves}.\n"
        win_msg += "Would you like to play a new game?"
        start_new = qwidget.QMessageBox.question(self, "You win!", win_msg)

        if start_new == qwidget.QMessageBox.StandardButton.Yes:
            print("New")
            self.start_new()
        # else:
        #     print("Exiting")
        #     self.close()

    def show_hint(self):
        start_coords, where_to_go_coords = self.logic.color_board.hint()
        self.button_grid[start_coords.row][start_coords.col].set_border(RED)
        self.button_grid[where_to_go_coords.row][where_to_go_coords.col].set_border(GREEN)

    def reset_hint(self):
        for row in self.button_grid:
            for btn in row:
                btn.set_border(btn.bg)

    def start_new(self):

        size_dialog = AskSize(self)
        size_dialog.exec()

        self.close()
        self.__init__(self.new_game_size, self.window_height, self.center)
        self.show()
        return self

    def save_image_palette(self):
        generator = self.logic.color_board.generator
        full_path, filename = self.generate_filename("png")
        generator.create_color_image(self.logic.solution, filename=full_path)
        self.show_file_saved_msg(filename)

    def generate_filename(self, extension: str) -> tuple[str, str]:
        # Get home directory, save to wherever Downloads are
        home = os.path.expanduser("~")
        filename = f"palette-{randint(0, 10000)}.{extension}"
        full_path = f"{home}/Downloads/{filename}"
        return full_path, filename

    def save_colors_hex(self):
        full_path, filename = self.generate_filename("txt")
        table = '\n'.join(['\t'.join([str(color) for color in row]) for row in self.logic.solution])
        with open(full_path, "w") as file:
            file.write(table)
        self.show_file_saved_msg(filename)

    def show_file_saved_msg(self, filename: str):
        saved_img_msg = qwidget.QMessageBox(self)
        saved_img_msg.setWindowTitle("Palette saved!")
        saved_img_msg.setText(f"The color palette was saved to Downloads as {filename}")
        saved_img_msg.exec()


def get_app_height_center(app: qwidget.QApplication) -> tuple[int, qcore.QPoint]:
    screen = app.primaryScreen()
    if screen:
        window_height = int(screen.geometry().height() * 0.8)
        center = screen.availableGeometry().center()
    else:
        window_height = DEFAULT_WINDOW_SIZE
        center = qcore.QPoint(0, 0)
    return window_height, center


if __name__ == "__main__":
    app = qwidget.QApplication(sys.argv)
    screen = app.primaryScreen()
    window_height, center = get_app_height_center(app)

    window = QBoard(int(sys.argv[1]), window_height, center)
    window.show()
    app.exec()
