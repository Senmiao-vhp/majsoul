import pytest
from src.core.player import Player
from src.core.hand import Hand
from src.core.player.state import PlayerState

def test_player_initialization():
    """测试Player类初始化"""
    player = Player("Test Player")
    assert player.name == "Test Player"
    assert isinstance(player.hand, Hand)
    assert len(player.hand.tiles) == 0
    assert player.points == 0

def test_player_points():
    """测试玩家分数操作"""
    player = Player("Test Player")
    # 测试设置分数
    player.set_points(25000)
    assert player.get_points() == 25000
    # 测试增加分数
    player.add_points(1000)
    assert player.get_points() == 26000

def test_player_hand_operations():
    """测试玩家手牌操作"""
    from src.core.tile import Tile, TileSuit
    
    player = Player("Test Player")
    tile = Tile(TileSuit.CHARACTERS, 1)
    
    # 测试摸牌
    player.hand.add_tile(tile)
    assert len(player.hand.tiles) == 1
    
    # 测试打牌
    discarded = player.hand.discard_tile(0)
    assert discarded == tile
    assert len(player.hand.tiles) == 0

def test_player_state():
    """测试玩家状态"""
    player = Player("Test Player")
    
    # 初始状态应该是WAITING
    assert player.state == PlayerState.WAITING
    
    # 切换到思考状态
    player.set_state(PlayerState.THINKING)
    assert player.state == PlayerState.THINKING
    
    # 切换到行动状态
    player.set_state(PlayerState.ACTING)
    assert player.state == PlayerState.ACTING