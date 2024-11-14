import pytest
from src.core.player import Player
from src.core.hand import Hand
from src.core.tile import Tile, TileSuit
from src.core.player.state import PlayerState

def test_player_initialization():
    """测试Player类初始化"""
    player = Player("Test Player")
    assert player.name == "Test Player"
    assert isinstance(player.hand, Hand)
    assert len(player.hand.tiles) == 0
    assert player.points == 25000
    assert not player.is_riichi

def test_player_points():
    """测试玩家分数操作"""
    player = Player("Test Player")
    player.set_points(25000)
    assert player.get_points() == 25000
    player.add_points(1000)
    assert player.get_points() == 26000

def test_player_discards():
    """测试玩家打出的牌"""
    player = Player("Test Player")
    tile = Tile(TileSuit.MAN, 1)
    
    # 添加并打出一张牌
    player.hand.add_tile(tile)
    discarded = player.discard_tile(0)
    
    assert discarded == tile
    assert len(player.discards) == 1
    assert player.discards[0] == tile