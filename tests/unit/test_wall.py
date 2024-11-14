import pytest
from src.core.wall import Wall
from src.core.tile import TileSuit

def test_wall_initialization():
    """测试牌墙初始化"""
    wall = Wall()
    assert wall.remaining_count == 136  # 总共136张牌
    
    # 验证牌的分布
    suit_counts = {
        TileSuit.MAN: 0,
        TileSuit.PIN: 0,
        TileSuit.SOU: 0,
        TileSuit.HONOR: 0
    }
    
    for tile in wall.tiles:
        suit_counts[tile.suit] += 1
    
    assert suit_counts[TileSuit.MAN] == 36
    assert suit_counts[TileSuit.PIN] == 36
    assert suit_counts[TileSuit.SOU] == 36
    assert suit_counts[TileSuit.HONOR] == 28

def test_wall_draw():
    """测试摸牌"""
    wall = Wall()
    initial_count = wall.remaining_count
    tile = wall.draw()
    
    assert tile is not None
    assert wall.remaining_count == initial_count - 1
    
    # 测试摸完所有牌
    while wall.remaining_count > 0:
        wall.draw()
    assert wall.draw() is None

def test_wall_shuffle():
    """测试洗牌"""
    wall1 = Wall()
    wall2 = Wall()
    
    # 记录初始牌序
    tiles1 = wall1.tiles.copy()
    tiles2 = wall2.tiles.copy()
    
    # 洗牌
    wall1.shuffle()
    wall2.shuffle()
    
    # 验证牌数没有变化
    assert len(wall1.tiles) == len(tiles1)
    assert len(wall2.tiles) == len(tiles2)
    
    # 验证牌序已经改变
    assert wall1.tiles != tiles1
    assert wall2.tiles != tiles2