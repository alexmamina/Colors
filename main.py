import PyQt6.QtCore as qcore
import PyQt6.QtWidgets as qwidget
import PyQt6.QtGui as qgui
import sys
from functools import partial
from typing import Optional, Callable
from math import floor
from random import randint
import os

from generators.color_logic import ColorLogic, Coordinates, PinnedPoints

DEFAULT_WINDOW_SIZE = 500
RED = "#ff0000"
GREEN = "#22ff00"
BLACK = "black"
WHITE = "white"
TITLE = "Väriaine"

BASEDIR = os.path.dirname(__file__)

# camelCase methods are inherited from PyQt6; snake_case methods are specific to the implementation


class ColorButton(qwidget.QPushButton):

    def __init__(
        self,
        parent: "QBoard",
        color: str,
        coords: Coordinates,
        window_height: int,
        btn_row_size: int,
    ):
        super(ColorButton, self).__init__()
        button_height = floor(window_height / btn_row_size)
        self.setAutoFillBackground(True)
        self.parent_board = parent
        self.coords = coords
        self.setMinimumSize(qcore.QSize(button_height, button_height))
        # Allow resizing buttons
        policy = qwidget.QSizePolicy.Policy.Minimum
        self.setSizePolicy(qwidget.QSizePolicy(policy, policy))
        self.fg = self.contrast_color(color)
        self.set_color(color)
        self.setAcceptDrops(self.parent_board.acceptDrops())

    def set_color(self, color: str):
        self.bg = color
        self.set_border(color)
        self.update_style()

    def set_border(self, border: str):
        self.border = f"2px solid {border}"
        self.update_style()

    def contrast_color(self, color: str) -> str:
        r, g, b = qgui.QColor(color).red(), qgui.QColor(color).green(), qgui.QColor(color).blue()
        brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return BLACK if brightness > 0.5 else WHITE

    def update_style(self):
        darker_shade = qgui.QColor(self.bg).darker(110).name()  # When clicked, button 10% darker
        contrast_border = self.contrast_color(self.bg)
        style = f"""
            QPushButton {{
                background-color: {self.bg};
                color: {self.fg};
                border: {self.border};
            }}
            QPushButton:checked {{
                background-color: {darker_shade};
                color: {self.fg};
                border: 2px solid {contrast_border};
            }}
        """
        self.setStyleSheet(style)

    def disable(self):
        img = qgui.QPixmap(os.path.join(BASEDIR, "images", "dot.png"))
        self.setIcon(qgui.QIcon(img))
        self.setIconSize(self.minimumSize())
        self.setEnabled(False)

    # Drag and drop events
    def select_and_swap(self, coords: Coordinates, e: Optional[qgui.QMouseEvent]) -> None:
        self.setChecked(True)
        self.parent_board.logic.select_and_swap(coords)

    def mouseMoveEvent(self, e: qgui.QMouseEvent):
        # Only move when we're accepting drops - i.e. have drag and drop enabled
        if e.buttons() == qcore.Qt.MouseButton.LeftButton and self.acceptDrops():
            drag = qgui.QDrag(self)
            mime = qcore.QMimeData()
            drag.setMimeData(mime)

            # Double the number of pixels to avoid blurring
            pixmap = qgui.QPixmap(self.size().width() * 2, self.size().height() * 2)
            pixmap.setDevicePixelRatio(2)
            self.render(pixmap)
            drag.setPixmap(pixmap)
            drag.setHotSpot(e.pos())

            drag.exec(qcore.Qt.DropAction.MoveAction)
            self.show()

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        self.parent_board.logic.select_and_swap(self.coords)
        e.accept()


class AskSize(qwidget.QDialog):
    def __init__(self, parent: "QBoard"):
        super().__init__(parent)

        self.setWindowTitle("New game!")

        message = qwidget.QLabel("Enter the size of the board (width of the square, defaults to 5)")

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
        # This is always true but the linter needs an extra check
        if parent and isinstance(parent, QBoard):
            number = int(self.input_number.text()) if self.input_number.text() else 5
            parent.game_size = number
        self.close()


class QBoard(qwidget.QMainWindow):
    def __init__(self, window_height: int, center: qcore.QPoint) -> None:
        # Initialise and center the board
        super().__init__()
        self.center = center
        self.window_height = window_height
        self.setAcceptDrops(True)
        self.set_title()
        shape = self.frameGeometry()
        shape.moveCenter(self.center)
        self.move(shape.topLeft())
        # icon = qgui.QPixmap("images/colors-icon.icns")
        self.setWindowIcon(qgui.QIcon(os.path.join(BASEDIR, "images", "colors-icon-rounded.icns")))

        # Get the game size
        self.game_size = 0
        size_dialog = AskSize(self)
        size_dialog.exec()

        self.setup_game()

    def set_title(self):
        mode = " (Drag and drop)" if self.acceptDrops() else " (Click)"
        self.setWindowTitle(TITLE + mode)
        print(f"Drag and drop is now: {self.acceptDrops()}")

    def setup_game(self):
        self.logic = ColorLogic(self.game_size, self)
        self.pinned_points = PinnedPoints(self.game_size)
        self.button_grid, self.button_holder = self.create_button_grid(self.game_size)
        self.setCentralWidget(self.button_holder)
        self.setup_toolbar()
        self.setMinimumSize(self.sizeHint())

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
            "Toggle drag and drop",
            "Click to swap or drag and drop colors",
            self.toggle_drag_and_drop,
        )

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
                color_button = ColorButton(self, color, coords, self.window_height, size)
                if not self.pinned_points.has(coords):
                    color_button.setCheckable(True)
                    color_button.mousePressEvent = partial(color_button.select_and_swap, coords)
                else:
                    color_button.disable()
                layout.addWidget(color_button, row, col)
                buttons[row].append(color_button)

        button_holder = qwidget.QWidget()
        button_holder.setLayout(layout)

        return buttons, button_holder

    def highlight_button(self, coords: Coordinates, color: str):
        self.button_grid[coords.row][coords.col].set_color(color)
        self.reset_selection(coords)

    def select_button(self, coords: Coordinates):
        self.button_grid[coords.row][coords.col].setChecked(True)

    def reset_selection(self, coords: Coordinates):
        self.button_grid[coords.row][coords.col].setChecked(False)

    def toggle_drag_and_drop(self):
        for row in self.button_grid:
            for button in row:
                button.setAcceptDrops(not button.acceptDrops())
        self.setAcceptDrops(not self.acceptDrops())
        self.set_title()

    def show_win(self, moves: Optional[int]):
        win_msg = "You win!\n"
        if moves:
            win_msg += f"Total moves taken: {moves}.\n"
        win_msg += "Would you like to play a new game?"
        new_game = qwidget.QMessageBox.question(self, "You win!", win_msg)

        if new_game == qwidget.QMessageBox.StandardButton.Yes:
            print("New")
            self.start_new()

    def show_hint(self):
        start_coords, where_to_go_coords = self.logic.color_board.hint()
        self.button_grid[start_coords.row][start_coords.col].set_border(RED)
        self.button_grid[where_to_go_coords.row][where_to_go_coords.col].set_border(GREEN)

    def reset_hint(self):
        for row in self.button_grid:
            for btn in row:
                btn.set_border(btn.bg)

    def start_new(self):
        self.close()
        self.__init__(self.window_height, self.center)
        self.show()

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

    window = QBoard(window_height, center)
    window.show()
    app.exec()
