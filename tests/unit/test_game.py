import pytest
from src.core.game import Game

def test_game_initialization():
    """测试Game类初始化"""
    game = Game()
    assert game is not None
    assert len(game.players) == 0
    assert game.rules is not None
    assert isinstance(game.config, dict)

def test_game_load_config():
    """测试游戏配置加载"""
    game = Game()
    assert game.get_player_count() == 4
    assert game.get_initial_points() == 25000
    assert game.get_version() == "1.0.0"

def test_game_initialize():
    """测试游戏初始化"""
    game = Game()
    assert game.initialize() is True
    assert len(game.players) == game.get_player_count()
    for player in game.players:
        assert player.get_points() == game.get_initial_points() 