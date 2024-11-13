import pytest
from src.core.tile import Tile, TileSuit

def test_tile_creation():
    """测试麻将牌创建"""
    tile = Tile(TileSuit.CHARACTERS, 5)
    assert tile.suit == TileSuit.CHARACTERS
    assert tile.value == 5
    assert tile.is_valid

def test_invalid_tile():
    """测试非法麻将牌"""
    tile = Tile(TileSuit.CHARACTERS, 10)
    assert not tile.is_valid 