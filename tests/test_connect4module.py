"""
Testes das regras do jogo (connect4module).

Para executar, a partir da raiz do projeto:

    python -m unittest discover -s tests -v
"""

import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import connect4module as c4  # noqa: E402


R = c4.PLAYER1_PIECE  # vermelha
Y = c4.PLAYER2_PIECE  # amarela


def draw_board():
    """Tabuleiro cheio, sem nenhuma sequência de 4 (empate)."""
    a = [R, R, Y, Y, R, R, Y]
    b = [Y, Y, R, R, Y, Y, R]
    return np.array([a, b, a, b, a, b], dtype=float)


class BoardBasicsTest(unittest.TestCase):

    def test_makearrayboard_is_empty_6x7(self):
        board = c4.makearrayboard()
        self.assertEqual(board.shape, (c4.ROWS, c4.COLUMNS))
        self.assertTrue((board == c4.EMPTY).all())

    def test_makemove_drops_piece_to_lowest_free_row(self):
        board = c4.makearrayboard()
        c4.makemove(board, 2, R)
        c4.makemove(board, 2, Y)
        self.assertEqual(board[5][2], R)
        self.assertEqual(board[4][2], Y)
        self.assertEqual(np.count_nonzero(board), 2)

    def test_makemove_on_full_column_changes_nothing(self):
        board = c4.makearrayboard()
        for _ in range(c4.ROWS):
            c4.makemove(board, 0, R)
        before = board.copy()
        c4.makemove(board, 0, Y)
        self.assertTrue((board == before).all())

    def test_wrappers_keep_original_piece_values(self):
        board = c4.makearrayboard()
        c4.dousermove(board, 0)
        c4.docomputermove(board, 1)
        self.assertEqual(board[5][0], 1)
        self.assertEqual(board[5][1], 5)

    def test_checkifvalid(self):
        board = c4.makearrayboard()
        self.assertTrue(c4.checkifvalid(board, 3))
        for _ in range(c4.ROWS):
            c4.makemove(board, 3, R)
        self.assertFalse(c4.checkifvalid(board, 3))

    def test_checkifvalid_rejects_out_of_range_columns(self):
        board = c4.makearrayboard()
        self.assertFalse(c4.checkifvalid(board, -1))
        self.assertFalse(c4.checkifvalid(board, c4.COLUMNS))


class GameStateTest(unittest.TestCase):

    def test_empty_board_is_ongoing(self):
        self.assertEqual(c4.checkgamestate(c4.makearrayboard()), c4.GAME_ONGOING)

    def _assert_win(self, cells, piece, expected_state, marker):
        board = c4.makearrayboard()
        for row, col in cells:
            board[row][col] = piece
        self.assertEqual(c4.checkgamestate(board), expected_state)
        for row, col in cells:
            self.assertEqual(board[row][col], marker)

    def test_wins_in_all_directions_for_both_pieces(self):
        lines = {
            "horizontal": [(5, 0), (5, 1), (5, 2), (5, 3)],
            "vertical": [(5, 6), (4, 6), (3, 6), (2, 6)],
            "diagonal_direita": [(5, 0), (4, 1), (3, 2), (2, 3)],
            "diagonal_esquerda": [(5, 6), (4, 5), (3, 4), (2, 3)],
        }
        for name, cells in lines.items():
            with self.subTest(direcao=name, peca="vermelha"):
                self._assert_win(cells, R, c4.PLAYER1_WINS, 100)
            with self.subTest(direcao=name, peca="amarela"):
                self._assert_win(cells, Y, c4.PLAYER2_WINS, 200)

    def test_three_in_a_row_is_not_a_win(self):
        board = c4.makearrayboard()
        for col in range(3):
            board[5][col] = R
        self.assertEqual(c4.checkgamestate(board), c4.GAME_ONGOING)

    def test_full_board_without_winner_is_draw(self):
        self.assertEqual(c4.checkgamestate(draw_board()), c4.DRAW)


class ComputerMoveTest(unittest.TestCase):

    def test_always_returns_existing_column(self):
        board = c4.makearrayboard()
        for _ in range(20):
            self.assertIn(c4.decidecomputermove(board), range(c4.COLUMNS))

    def test_blocks_vertical_threat(self):
        board = c4.makearrayboard()
        for row in (5, 4, 3):
            board[row][0] = R
        self.assertEqual(c4.decidecomputermove(board), 0)

    def test_blocks_horizontal_threat(self):
        board = c4.makearrayboard()
        for col in (1, 2, 3):
            board[5][col] = R
        self.assertIn(c4.decidecomputermove(board), (0, 4))

    def test_prefers_winning_over_blocking(self):
        board = c4.makearrayboard()
        for row in (5, 4, 3):
            board[row][0] = R
            board[row][6] = Y
        self.assertEqual(c4.decidecomputermove(board), 6)


class LocalMatchTest(unittest.TestCase):

    def test_starts_with_chosen_player(self):
        self.assertEqual(c4.LocalMatch().current_player, 1)
        self.assertEqual(c4.LocalMatch(first_player=2).current_player, 2)

    def test_rejects_invalid_first_player(self):
        with self.assertRaises(ValueError):
            c4.LocalMatch(first_player=3)

    def test_turns_alternate_and_pieces_match_player(self):
        match = c4.LocalMatch()
        self.assertEqual(match.play(0), c4.MOVE_OK)
        self.assertEqual(match.current_player, 2)
        self.assertEqual(match.play(0), c4.MOVE_OK)
        self.assertEqual(match.current_player, 1)
        self.assertEqual(match.board[5][0], R)
        self.assertEqual(match.board[4][0], Y)

    def test_player2_starting_uses_yellow_pieces(self):
        match = c4.LocalMatch(first_player=2)
        match.play(3)
        self.assertEqual(match.board[5][3], Y)

    def test_invalid_moves_do_not_change_board_or_turn(self):
        match = c4.LocalMatch()
        for _ in range(c4.ROWS):
            match.play(0)
        board_before = match.board.copy()
        player_before = match.current_player

        cases = [
            (lambda: match.play(0), c4.MOVE_COLUMN_FULL),
            (lambda: match.play(-1), c4.MOVE_INVALID_COLUMN),
            (lambda: match.play(c4.COLUMNS), c4.MOVE_INVALID_COLUMN),
            (lambda: match.play(1, player=3 - player_before), c4.MOVE_WRONG_TURN),
        ]
        for attempt, expected in cases:
            with self.subTest(esperado=expected):
                self.assertEqual(attempt(), expected)
                self.assertTrue((match.board == board_before).all())
                self.assertEqual(match.current_player, player_before)

    def test_play_accepts_explicit_correct_player(self):
        match = c4.LocalMatch()
        self.assertEqual(match.play(0, player=1), c4.MOVE_OK)

    def test_vertical_win_ends_match_and_blocks_new_moves(self):
        match = c4.LocalMatch()
        for _ in range(3):
            match.play(0)  # Jogador 1
            match.play(6)  # Jogador 2
        self.assertFalse(match.finished)
        self.assertEqual(match.play(0), c4.MOVE_OK)

        self.assertTrue(match.finished)
        self.assertEqual(match.state, c4.PLAYER1_WINS)
        self.assertEqual(match.winner, 1)
        self.assertEqual(match.current_player, 1)

        board_before = match.board.copy()
        self.assertEqual(match.play(1), c4.MOVE_GAME_OVER)
        self.assertTrue((match.board == board_before).all())

    def test_player2_can_win(self):
        match = c4.LocalMatch()
        for col in (0, 1, 0, 1, 0, 1, 5):
            match.play(col)
        self.assertEqual(match.play(1), c4.MOVE_OK)
        self.assertEqual(match.winner, 2)

    def test_last_move_filling_board_is_draw(self):
        match = c4.LocalMatch(first_player=2)
        match.board = draw_board()
        match.board[0][6] = c4.EMPTY  # a última casa é de uma peça amarela
        self.assertEqual(match.play(6), c4.MOVE_OK)
        self.assertEqual(match.state, c4.DRAW)
        self.assertTrue(match.finished)
        self.assertIsNone(match.winner)


if __name__ == "__main__":
    unittest.main()
