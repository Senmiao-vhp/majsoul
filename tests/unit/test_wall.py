import pytest
from src.core.wall import Wall
from src.core.tile import TileSuit

def test_wall_initialization():
    """测试牌墙初始化"""
    wall = Wall()
    assert wall.get_remaining_count() == 136  # 总共136张牌
    
def test_wall_draw():
    """测试摸牌"""
    wall = Wall()
    initial_count = wall.get_remaining_count()
    tile = wall.draw()
    assert tile is not None
    assert wall.get_remaining_count() == initial_count - 1 