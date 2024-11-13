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