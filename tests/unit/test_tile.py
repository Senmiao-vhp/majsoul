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

def test_tile_comparison():
    """测试麻将牌比较"""
    tile1 = Tile(TileSuit.CHARACTERS, 1)
    tile2 = Tile(TileSuit.CHARACTERS, 2)
    tile3 = Tile(TileSuit.BAMBOO, 1)
    tile4 = Tile(TileSuit.CHARACTERS, 1, True)  # 赤牌
    
    # 测试相等
    assert tile1 == Tile(TileSuit.CHARACTERS, 1)
    assert tile1 != tile4  # 赤牌不等于普通牌
    
    # 测试大小比较
    assert tile1 < tile2  # 同花色不同数值
    assert tile1 < tile3  # 不同花色
    assert not tile2 < tile1  # 反向比较
    
def test_tile_hash():
    """测试麻将牌哈希"""
    tile1 = Tile(TileSuit.CHARACTERS, 1)
    tile2 = Tile(TileSuit.CHARACTERS, 1)
    tile3 = Tile(TileSuit.CHARACTERS, 1, True)  # 赤牌
    
    # 相同牌应该有相同的哈希值
    assert hash(tile1) == hash(tile2)
    # 赤牌应该有不同的哈希值
    assert hash(tile1) != hash(tile3)
    
    # 测试作为字典键
    tile_dict = {tile1: "normal", tile3: "red"}
    assert len(tile_dict) == 2
    assert tile_dict[tile1] == "normal"
    assert tile_dict[tile3] == "red"
    
def test_tile_string_representation():
    """测试麻将牌字符串表示"""
    tile1 = Tile(TileSuit.CHARACTERS, 5)
    tile2 = Tile(TileSuit.CHARACTERS, 5, True)
    
    assert str(tile1) == "万5"
    assert str(tile2) == "万5红" 