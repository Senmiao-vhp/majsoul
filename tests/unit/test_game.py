import pytest
from src.core.game import Game
from src.core.game.state import GameState

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

def test_game_state_transitions():
    """测试游戏状态转换"""
    game = Game()
    
    # 初始状态应该是WAITING
    assert game.get_state() == GameState.WAITING
    
    # 初始化游戏
    game.initialize()
    assert game.get_state() == GameState.WAITING
    
    # 开始游戏
    game.start()
    assert game.get_state() == GameState.DEALING
    
    # 发牌完成
    game.set_state(GameState.PLAYING)
    assert game.get_state() == GameState.PLAYING
    
    # 游戏结束
    game.set_state(GameState.FINISHED)
    assert game.get_state() == GameState.FINISHED 