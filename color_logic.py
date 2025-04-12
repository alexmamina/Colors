from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from main import QBoard
from random import randint, sample
from hsl_color_generator import ColorGenerator


@dataclass
class Coordinates:
    row: int
    col: int

    @classmethod
    def random(cls, size: int) -> "Coordinates":
        from_coords = Coordinates(randint(0, size - 1), randint(0, size - 1))
        while PinnedPoints(size).has(from_coords):
            from_coords = Coordinates(randint(0, size - 1), randint(0, size - 1))
        return from_coords

    def pretty(self):
        print(f"Row {self.row}, column {self.col}")


@dataclass
class PinnedPoints:
    board_size: int

    def __post_init__(self):
        # Pick the number of pinned points for the board size: 1 for size 2, 3 for size 3, 4 for 4+
        self.TOPLEFT = Coordinates(0, 0)
        self.TOPRIGHT = Coordinates(0, self.board_size - 1)
        self.BOTTOMLEFT = Coordinates(self.board_size - 1, 0)
        self.BOTTOMRIGHT = Coordinates(self.board_size - 1, self.board_size - 1)

    def get_fields_from_points(self, board: "Board") -> tuple[str, str, str, str]:
        top_left = board.get_solution_cell(self.TOPLEFT)
        top_right = board.get_solution_cell(self.TOPRIGHT)
        bottom_left = board.get_solution_cell(self.BOTTOMLEFT)
        bottom_right = board.get_solution_cell(self.BOTTOMRIGHT)
        return top_left, top_right, bottom_left, bottom_right

    def has(self, coords: Coordinates) -> bool:
        equals = coords == self.TOPLEFT or \
            coords == self.TOPRIGHT or \
            coords == self.BOTTOMLEFT or \
            coords == self.BOTTOMRIGHT
        return equals


class Board:
    def __init__(self, size: int):
        assert size > 2, "The width of the board must be greater than 2 colors!"
        self.size = size
        self.generator = ColorGenerator(size)
        self.solution = self.generator.generate_initial_color_board(self.size)
        self.board = self.shuffle_board_from_solution()

    def shuffle_board_from_solution(self) -> list[list[str]]:
        corner_points = PinnedPoints(self.size).get_fields_from_points(self)
        colors = self.flatten_board(self.solution)
        # The analog of a 'shuffle' - sample N random colors from a list where N is just all of them
        shuffled_colors = sample(colors, len(colors))
        # Remove corner points from the shuffled list to set them explicitly
        for point in corner_points:
            shuffled_colors.pop(shuffled_colors.index(point))
        color_board = []
        for row in range(self.size):
            new_row = []
            for col in range(self.size):
                if row == 0 and col == 0:
                    new_row.append(corner_points[0])
                elif row == 0 and col == self.size - 1:
                    new_row.append(corner_points[1])
                elif row == self.size - 1 and col == 0:
                    new_row.append(corner_points[2])
                elif row == self.size - 1 and col == self.size - 1:
                    new_row.append(corner_points[3])
                else:
                    new_row.append(shuffled_colors.pop())
            color_board.append(new_row)
        print(color_board)
        return color_board

    def check_solved(self) -> bool:
        return self.solution == self.board

    def get_cell(self, coords: Coordinates):
        return self.board[coords.row][coords.col]

    def get_solution_cell(self, coords: Coordinates):
        return self.solution[coords.row][coords.col]

    def set_color(self, coords: Coordinates, color: str):
        self.board[coords.row][coords.col] = color

    def hint(self) -> tuple[Coordinates, Coordinates]:
        first_coords = Coordinates.random(self.size)
        first_color = self.get_cell(first_coords)
        where_to_place = self.find_coords_of_color(self.solution, first_color)
        while first_coords == where_to_place:
            first_coords = Coordinates.random(self.size)
            first_color = self.get_cell(first_coords)
            where_to_place = self.find_coords_of_color(self.solution, first_color)
        return first_coords, where_to_place

    def find_coords_of_color(self, board: list[list[str]], color: str) -> Coordinates:
        for row_ind in range(self.size):
            for col_ind in range(self.size):
                if board[row_ind][col_ind] == color:
                    return Coordinates(row_ind, col_ind)
        return Coordinates(0, 0)

    def flatten_board(self, board: list[list[str]]) -> list[str]:
        result = []
        for row in board:
            result += row
        return result


class ColorLogic:
    def __init__(self, board_size: int, ui: "QBoard", show_total_moves: bool = True):
        self.board_size = board_size
        self.color_board = Board(board_size)
        self.selected: Optional[Coordinates] = None
        self.total_moves = 0
        self.solution = self.color_board.solution
        self.completed: bool = False
        self.show_total_moves = show_total_moves
        self.ui = ui

    def select_and_swap(self, coords: Coordinates):
        if not self.selected:
            self.selected = coords
        elif self.selected == coords:
            self.selected = None
        else:
            first_color = self.color_board.get_cell(self.selected)
            second_color = self.color_board.get_cell(coords)
            self.color_board.set_color(self.selected, second_color)
            self.color_board.set_color(coords, first_color)
            self.total_moves += 1
            self.ui.highlight_button(self.selected, second_color)
            self.ui.highlight_button(coords, first_color)
            self.selected = None
            if self.color_board.check_solved():
                self.completed = True
                self.show_win()

    def show_win(self):
        win_str = "Congrats!"
        if self.show_total_moves:
            total_moves_str = "moves" if self.total_moves > 1 else "move"
            win_str += f" You have taken {self.total_moves} {total_moves_str} to complete the game"
        print(win_str)
        self.ui.show_win(self.total_moves)
