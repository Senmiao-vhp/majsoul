import pytest
from src.core.game import Game
from src.core.game.state import GameState
from src.core.player.state import PlayerState
from src.core.rules import Rules

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

def test_handle_tile_click():
    """测试牌点击处理"""
    game = Game()
    game.initialize()
    game.start()
    game.set_state(GameState.PLAYING)
    
    # 获取当前玩家并设置状态
    current_player = game.table.get_current_player()
    current_player.set_state(PlayerState.THINKING)
    initial_tiles = len(current_player.hand.tiles)
    
    # 测试有效点击
    assert game.handle_tile_click(0) is True
    assert len(current_player.hand.tiles) == initial_tiles
    assert current_player.selected_tile_index == 0
    
    # 测试无效点击（索引越界）
    game.handle_tile_click(100)
    assert len(current_player.hand.tiles) == initial_tiles

def test_skip_current_action():
    """测试跳过当前操作"""
    game = Game()
    game.initialize()
    game.start()
    
    # 非PLAYING状态下跳过
    initial_player = game.table.get_current_player()
    game.skip_current_action()
    assert game.table.get_current_player() == initial_player
    
    # PLAYING状态下跳过
    game.set_state(GameState.PLAYING)
    game.skip_current_action()
    assert game.table.get_current_player() != initial_player 

def test_rules_init():
    """测试Rules类初始化"""
    rules = Rules()
    assert isinstance(rules.config, dict)
    assert rules.get_tile_count() == 136

def test_validate_points():
    """测试点数验证"""
    rules = Rules()
    assert rules.validate_points(1) is True
    assert rules.validate_points(13) is True
    assert rules.validate_points(0) is False
    assert rules.validate_points(14) is False 