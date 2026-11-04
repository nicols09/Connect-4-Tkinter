"""Testes de importação e recursos opcionais da interface."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gamegui  # noqa: E402


class GameGuiImportTest(unittest.TestCase):

    def test_gui_imports_without_windows_audio_backend(self):
        self.assertTrue(hasattr(gamegui, "Connect4App"))

    def test_coin_faces_are_available(self):
        faces = gamegui.load_coin_faces()
        self.assertIsNotNone(faces)
        self.assertEqual(len(faces), 2)


if __name__ == "__main__":
    unittest.main()