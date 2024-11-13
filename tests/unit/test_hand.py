import pytest
from src.core.hand import Hand
from src.core.tile import Tile, TileSuit

def test_hand_operations():
    """测试手牌操作"""
    hand = Hand()
    tile = Tile(TileSuit.CHARACTERS, 5)
    
    # 测试添加牌
    hand.add_tile(tile)
    assert len(hand.tiles) == 1
    
    # 测试打出牌
    discarded = hand.discard_tile(0)
    assert discarded == tile
    assert len(hand.tiles) == 0 

def test_hand_melds():
    """测试手牌副露"""
    hand = Hand()
    
    # 创建一组副露牌
    tiles = [
        Tile(TileSuit.CHARACTERS, 1),
        Tile(TileSuit.CHARACTERS, 1),
        Tile(TileSuit.CHARACTERS, 1)
    ]
    
    # 添加副露
    hand.add_meld(tiles)
    assert len(hand.melds) == 1
    assert len(hand.melds[0]) == 3
    
    # 验证副露内容
    meld = hand.melds[0]
    for tile in meld:
        assert tile.suit == TileSuit.CHARACTERS
        assert tile.value == 1

def test_remove_tile():
    """测试移除手牌"""
    hand = Hand()
    tile = Tile(TileSuit.CHARACTERS, 1)
    
    # 添加牌
    hand.add_tile(tile)
    assert len(hand.tiles) == 1
    
    # 移除牌
    hand.discard_tile(0)
    assert len(hand.tiles) == 0
    
    # 移除不存在的牌
    hand.discard_tile(0)  # 不应该抛出异常
    assert len(hand.tiles) == 0

def test_check_tenpai():
    """测试听牌检测"""
    hand = Hand()
    
    # 添加一个听牌型
    tiles = [
        Tile(TileSuit.CHARACTERS, 1), Tile(TileSuit.CHARACTERS, 1),
        Tile(TileSuit.CHARACTERS, 2), Tile(TileSuit.CHARACTERS, 2),
        Tile(TileSuit.CHARACTERS, 3), Tile(TileSuit.CHARACTERS, 3),
        Tile(TileSuit.CHARACTERS, 4), Tile(TileSuit.CHARACTERS, 4),
        Tile(TileSuit.CHARACTERS, 5), Tile(TileSuit.CHARACTERS, 5),
        Tile(TileSuit.CHARACTERS, 6), Tile(TileSuit.CHARACTERS, 6),
        Tile(TileSuit.CHARACTERS, 7)
    ]
    
    for tile in tiles:
        hand.add_tile(tile)
        
    waiting_tiles = hand.check_tenpai()
    assert len(waiting_tiles) == 1
    assert waiting_tiles[0] == Tile(TileSuit.CHARACTERS, 7)

def test_check_win():
    """测试和牌判定"""
    hand = Hand()
    
    # 测试七对子和牌
    tiles = [
        Tile(TileSuit.CHARACTERS, 1), Tile(TileSuit.CHARACTERS, 1),
        Tile(TileSuit.CHARACTERS, 2), Tile(TileSuit.CHARACTERS, 2),
        Tile(TileSuit.CHARACTERS, 3), Tile(TileSuit.CHARACTERS, 3),
        Tile(TileSuit.CHARACTERS, 4), Tile(TileSuit.CHARACTERS, 4),
        Tile(TileSuit.CHARACTERS, 5), Tile(TileSuit.CHARACTERS, 5),
        Tile(TileSuit.CHARACTERS, 6), Tile(TileSuit.CHARACTERS, 6),
        Tile(TileSuit.CHARACTERS, 7)
    ]
    
    for tile in tiles:
        hand.add_tile(tile)
        
    assert hand.check_win(Tile(TileSuit.CHARACTERS, 7))
    
def test_check_thirteen_orphans():
    """测试国士无双和牌"""
    hand = Hand()
    
    # 添加所有幺九牌
    tiles = [
        Tile(TileSuit.CHARACTERS, 1), Tile(TileSuit.CHARACTERS, 9),
        Tile(TileSuit.CIRCLES, 1), Tile(TileSuit.CIRCLES, 9),
        Tile(TileSuit.BAMBOO, 1), Tile(TileSuit.BAMBOO, 9),
        # 字牌
        Tile(TileSuit.HONOR, 1), Tile(TileSuit.HONOR, 2),
        Tile(TileSuit.HONOR, 3), Tile(TileSuit.HONOR, 4),
        Tile(TileSuit.HONOR, 5), Tile(TileSuit.HONOR, 6),
        Tile(TileSuit.HONOR, 7)
    ]
    
    for tile in tiles:
        hand.add_tile(tile)
        
    assert hand.check_win(tiles[0])

def test_check_normal_win():
    """测试普通和牌型"""
    hand = Hand()
    
    # 添加一个基本和牌型(一杯口)
    tiles = [
        # 雀头
        Tile(TileSuit.CHARACTERS, 1), Tile(TileSuit.CHARACTERS, 1),
        # 顺子1
        Tile(TileSuit.CHARACTERS, 2), Tile(TileSuit.CHARACTERS, 3), Tile(TileSuit.CHARACTERS, 4),
        # 顺子2
        Tile(TileSuit.CHARACTERS, 2), Tile(TileSuit.CHARACTERS, 3), Tile(TileSuit.CHARACTERS, 4),
        # 刻子
        Tile(TileSuit.CIRCLES, 5), Tile(TileSuit.CIRCLES, 5), Tile(TileSuit.CIRCLES, 5),
        # 顺子3
        Tile(TileSuit.BAMBOO, 7), Tile(TileSuit.BAMBOO, 8)
    ]
    
    for tile in tiles:
        hand.add_tile(tile)
        
    # 测试和牌
    assert hand.check_win(Tile(TileSuit.BAMBOO, 9))