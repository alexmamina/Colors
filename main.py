import sys
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from qtb import QBoard
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
        bottom__right = board.get_solution_cell(self.BOTTOMRIGHT)
        return top_left, top_right, bottom_left, bottom__right

    def has(self, coords: Coordinates) -> bool:
        equals = coords == self.TOPLEFT or \
            coords == self.TOPRIGHT or \
            coords == self.BOTTOMLEFT or \
            coords == self.BOTTOMRIGHT
        return equals


class Board:
    def __init__(self, size: int):
        self.size = size
        self.generator = ColorGenerator(size)
        self.solution = self.generator.generate_initial_color_board(self.size)
        self.board = self.shuffle_board_from_solution()

    def shuffle_board_from_solution(self) -> list[list[str]]:
        pin_tl, pin_tr, pin_bl, pin_br = PinnedPoints(self.size).get_fields_from_points(self)
        colors = self.flatten_board(self.solution)
        ind_tl = colors.index(pin_tl)
        ind_tr = colors.index(pin_tr)
        ind_bl = colors.index(pin_bl)
        ind_br = colors.index(pin_br)

        shuffled_pinned_colors = [pin_tl] + \
            sample(colors[ind_tl + 1: ind_tr], len(colors[ind_tl + 1: ind_tr])) + [pin_tr] + \
            sample(colors[ind_tr + 1: ind_bl], len(colors[ind_tr + 1: ind_bl])) + [pin_bl] + \
            sample(colors[ind_bl + 1: ind_br], len(colors[ind_bl + 1: ind_br])) + [pin_br]
        print(shuffled_pinned_colors)

        assert shuffled_pinned_colors.index(pin_tl) == ind_tl and \
            shuffled_pinned_colors.index(pin_tr) == ind_tr and \
            shuffled_pinned_colors.index(pin_bl) == ind_bl and \
            shuffled_pinned_colors.index(pin_br) == ind_br
        return self.from_list(shuffled_pinned_colors)

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

    def from_list(self, color_list: list[str]) -> list[list[str]]:
        board = []
        for i in range(self.size):
            board.append(color_list[i * self.size:i * self.size + self.size])
        return board

    def pretty(self):
        for row in self.board:
            print(row)
        print()


class ColorLogic:
    def __init__(self, board_size: int, ui: "Optional[QBoard]", show_total_moves: bool = True):
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

    def loop(self):
        finish = False
        while not self.completed and not finish:
            self.color_board.pretty()
            if self.selected:
                self.selected.pretty()
            string_coords = self.get_input(
                "Print row, column coordinates separated by space to select a cell to swap"
            )
            if string_coords == 'n':
                finish = True
            else:
                try:
                    row, column = int(string_coords.split()[0]), int(string_coords.split()[1])
                except (ValueError, IndexError):
                    print("Invalid number!")
                    continue
                if row >= self.board_size or column >= self.board_size:
                    print("Number too big!")
                    continue
                coords = Coordinates(row, column)
                self.select_and_swap(coords)
        if self.completed:
            self.show_win()

    def get_input(self, question: str) -> str:
        question += " or enter n to exit\n"
        return input(question)


if __name__ == "__main__":

    try:
        size = int(sys.argv[1])
    except (KeyError, ValueError):
        print("Please enter a valid number for the board size!")
        sys.exit(1)

    # todo Generate colors (4 points of reference with a gradient - limit to brighter/pastel/nicer
    # colors?)

    # todo rectangle
