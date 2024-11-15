from src.core.tile import Tile, TileSuit
from src.core.river import River

def test_river():
    """测试牌河功能"""
    river = River()
    
    # 测试添加牌
    tile1 = Tile(TileSuit.MAN, 1)
    tile2 = Tile(TileSuit.PIN, 2)
    river.add_tile(tile1, True)  # 摸切
    river.add_tile(tile2, False)  # 手切
    
    assert len(river.get_tiles()) == 2
    assert river.is_tsumogiri(0) == True
    assert river.is_tsumogiri(1) == False
    
    # 测试立直标记
    river.mark_riichi()
    assert river.riichi_tile_index == 1
    
    # 测试清空
    river.clear()
    assert len(river.get_tiles()) == 0