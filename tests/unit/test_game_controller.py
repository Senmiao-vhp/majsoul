import pytest
from src.core.game.controller import GameController
from src.core.table import Table
from src.core.player import Player
from src.core.game.state import GameState
from src.core.player.state import PlayerState
def test_game_controller_init():
    """测试游戏控制器初始化"""
    table = Table()
    controller = GameController(table)
    assert controller.state == GameState.WAITING
    
def test_game_start():
    """测试游戏开始"""
    table = Table()
    controller = GameController(table)
    
    # 添加玩家
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
        
    assert controller.start_game() is True
    assert controller.state == GameState.DEALING
    
    # 手动切换到PLAYING状态
    controller.state = GameState.PLAYING
    
def test_turn_processing():
    """测试回合处理"""
    table = Table()
    controller = GameController(table)
    
    # 添加玩家并开始游戏
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
    controller.start_game()
    
    # 确保状态为PLAYING
    controller.state = GameState.PLAYING
    
    # 测试回合处理
    current_player = table.get_current_player()
    initial_tiles = len(current_player.hand.tiles)
    controller.process_turn(current_player)
    assert len(current_player.hand.tiles) == initial_tiles + 1