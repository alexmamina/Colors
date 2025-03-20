import unittest.mock
import main
import unittest
from color_generator import ColorGenerator


class Tests(unittest.TestCase):

    def setUp(self) -> None:
        self.size = 3
        self.logic = main.ColorLogic(self.size, None)
        self.r = 1
        self.c = 2
        self.selection = str(self.r * self.size + self.c + 1)
        self.coords = main.Coordinates(self.r, self.c)

        self.r2 = 0
        self.c2 = 1
        self.selection2 = str(self.r2 * self.size + self.c2 + 1)
        self.coords2 = main.Coordinates(self.r2, self.c2)
        self.board_test = [
            [str(i * self.size + j + 1) for j in range(self.size)] for i in range(self.size)
        ]

    def test_board_existence(self):
        self.assertEqual(self.logic.color_board.board, self.board_test)

    def test_selected_nothing(self):
        self.assertEqual(self.logic.selected, None)

    def test_selected_once(self):
        self.logic.select_and_swap(self.coords)
        self.assertEqual(self.logic.selected, self.coords)
        self.assertEqual(self.logic.total_moves, 0)

    def test_correct_color(self):
        color = self.logic.color_board.get_cell(self.coords)
        self.assertEqual(color, '#000000')

    def test_set_color(self):
        color = '#000000'
        self.logic.color_board.set_color(self.coords, color)
        new_color = self.logic.color_board.get_cell(self.coords)
        self.assertEqual(new_color, color)
        self.board_test[self.coords.row][self.coords.col] = '#000000'
        self.assertEqual(self.logic.color_board.board, self.board_test)

    def test_unselected(self):
        self.logic.select_and_swap(self.coords)
        self.logic.select_and_swap(self.coords)
        self.assertEqual(self.logic.selected, None)
        self.assertEqual(self.logic.total_moves, 0)

    def test_swapped(self):
        self.logic.select_and_swap(self.coords)
        self.logic.select_and_swap(self.coords2)
        result_board = [['1', '6', '3'], ['4', '5', '2'], ['7', '8', '9']]
        self.assertEqual(self.logic.color_board.board, result_board)
        self.assertEqual(self.logic.total_moves, 1)

    # def test_many_swapped(self):
    #     for _ in range(3):  # Swap, swap back, swap again
    #         self.logic.select_and_swap(self.coords)
    #         self.logic.select_and_swap(self.coords2)
    #     result_board = [['1', '6', '3'], ['4', '5', '2'], ['7', '8', '9']]
    #     self.assertEqual(self.logic.color_board.board, result_board)
    #     self.assertEqual(self.logic.total_moves, 3)

    def test_solution(self):
        self.logic.select_and_swap(self.coords)
        self.logic.select_and_swap(self.coords2)
        self.assertFalse(self.logic.color_board.check_solved())

    def test_shuffle_not_equal(self):
        self.assertFalse(self.logic.color_board.check_solved())

    def test_flatten(self):
        b = [['1', '6', '3'], ['4', '5', '2'], ['7', '8', '9']]
        result = ['1', '6', '3', '4', '5', '2', '7', '8', '9']
        self.assertEqual(self.logic.color_board.flatten_board(b), result)

    def test_unflatten(self):
        b = [['1', '6', '3'], ['4', '5', '2'], ['7', '8', '9']]
        result = ['1', '6', '3', '4', '5', '2', '7', '8', '9']
        self.assertEqual(self.logic.color_board.from_list(result), b)

    def test_coords_of_color(self):
        # b = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
        find = self.logic.color_board.find_coords_of_color(self.logic.solution, "6")
        coords = main.Coordinates(1, 2)
        self.assertEqual(find, coords)

    def test_no_coords_of_color(self):
        # [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
        find = self.logic.color_board.find_coords_of_color(self.logic.solution, "16")
        coords = main.Coordinates(0, 0)
        self.assertEqual(find, coords)

    def test_coords_board(self):
        color = "6"
        coords = self.logic.color_board.find_coords_of_color(self.logic.color_board.board, color)
        color_in_coords = self.logic.color_board.get_cell(coords)
        self.assertEqual(color, color_in_coords)

    def test_linear_gradient(self):
        for i in range(10000):
            for size in range(2, 50):
                with self.subTest(msg=size, params=size):
                    generator = ColorGenerator(self.size)
                    color1 = generator.random_color()
                    color2 = generator.random_color()
                    generator.linear_gradient(color1, color2, size)
            if i % 2000 == 0:
                print(f"{i} done!")
