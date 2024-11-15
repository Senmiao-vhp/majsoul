import pytest
from src.core.tile import Tile, TileSuit

def test_tile_creation():
    """测试麻将牌创建"""
    tile = Tile(TileSuit.MAN, 5)
    assert tile.suit == TileSuit.MAN
    assert tile.value == 5
    assert tile.is_valid

def test_invalid_tile():
    """测试非法麻将牌"""
    tile = Tile(TileSuit.MAN, 10)
    assert not tile.is_valid

def test_tile_comparison():
    """测试麻将牌比较"""
    tile1 = Tile(TileSuit.MAN, 1)
    tile2 = Tile(TileSuit.MAN, 2)
    tile3 = Tile(TileSuit.SOU, 1)
    tile4 = Tile(TileSuit.MAN, 1, True)  # 赤牌
    
    # 测试相等
    assert tile1 == Tile(TileSuit.MAN, 1)
    assert tile1 != tile4  # 赤牌不等于普通牌
    
    # 测试大小比较
    assert tile1 < tile2  # 同花色不同数值
    assert tile1 < tile3  # 不同花色
    assert not tile2 < tile1  # 反向比较
    
def test_tile_hash():
    """测试麻将牌哈希"""
    tile1 = Tile(TileSuit.MAN, 1)
    tile2 = Tile(TileSuit.MAN, 1)
    tile3 = Tile(TileSuit.MAN, 1, True)  # 赤牌
    
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
    tile1 = Tile(TileSuit.MAN, 5)
    tile2 = Tile(TileSuit.MAN, 5, True)
    
    assert str(tile1) == "万5"
    assert str(tile2) == "万5红"

def test_tile_34_index():
    """测试34编码索引转换"""
    # 测试万子
    assert Tile(TileSuit.MAN, 1).get_34_index() == 0
    assert Tile(TileSuit.MAN, 9).get_34_index() == 8
    
    # 测试筒子
    assert Tile(TileSuit.PIN, 1).get_34_index() == 9
    assert Tile(TileSuit.PIN, 9).get_34_index() == 17
    
    # 测试索子
    assert Tile(TileSuit.SOU, 1).get_34_index() == 18
    assert Tile(TileSuit.SOU, 9).get_34_index() == 26
    
    # 测试字牌
    assert Tile(TileSuit.HONOR, 1).get_34_index() == 27  # 东
    assert Tile(TileSuit.HONOR, 7).get_34_index() == 33  # 中
    
    # 测试非法牌
    with pytest.raises(ValueError):
        Tile(TileSuit.HONOR, 8).get_34_index() 

def test_aka_dora_validation():
    """测试赤宝牌验证"""
    # 有效的赤宝牌
    assert Tile(TileSuit.MAN, 5, True).is_valid  # 赤5万
    assert Tile(TileSuit.PIN, 5, True).is_valid  # 赤5筒
    assert Tile(TileSuit.SOU, 5, True).is_valid  # 赤5索
    
    # 无效的赤宝牌
    assert not Tile(TileSuit.MAN, 1, True).is_valid  # 非5的赤牌
    assert not Tile(TileSuit.HONOR, 5, True).is_valid  # 字牌不能是赤牌