from src.core.tile import Tile, TileSuit
from src.core.converter import TileConverter


def test_tile_converter():
    """测试牌格式转换"""
    # 创建测试用牌
    tiles = [
        Tile(TileSuit.MAN, 1),
        Tile(TileSuit.PIN, 2),
        Tile(TileSuit.SOU, 3),
        Tile(TileSuit.HONOR, 1)
    ]
    
    # 测试转换
    tiles_136 = TileConverter.to_136_array(tiles)
    assert len(tiles_136) == 4
    
    # 测试赤宝牌
    aka_tiles = [Tile(TileSuit.MAN, 5, True)]
    aka_136 = TileConverter.to_136_array(aka_tiles, has_aka_dora=True)
    assert len(aka_136) == 1 