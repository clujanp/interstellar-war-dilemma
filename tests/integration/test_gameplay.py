from unittest import TestCase
from app.main import game_loop


class TestGameplay(TestCase):
    def setUp(self):
        self.game = game_loop()

    def tearDown(self):
        ...

    def test_game(self): 
        ...
