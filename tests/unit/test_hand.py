import pytest
from src.core.hand import Hand
from src.core.tile import Tile, TileSuit
from src.core.player import Player

def test_hand_operations():
    """测试手牌操作"""
    player = Player("Test")
    hand = Hand(player)
    tile = Tile(TileSuit.MAN, 5)
    
    # 测试添加牌
    hand.add_tile(tile)
    assert len(hand.tiles) == 1
    
    # 测试打出牌
    discarded = hand.discard_tile(0)
    assert discarded == tile
    assert len(hand.tiles) == 0 

def test_hand_melds():
    """测试手牌副露"""
    player = Player("Test")
    hand = Hand(player)
    
    # 创建一组副露牌
    tiles = [
        Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 1)
    ]
    
    # 添加副露
    hand.add_meld(tiles)
    assert len(hand.melds) == 1
    assert len(hand.melds[0]) == 3
    
    # 验证副露内容
    meld = hand.melds[0]
    for tile in meld:
        assert tile.suit == TileSuit.MAN
        assert tile.value == 1

def test_remove_tile():
    """测试移除手牌"""
    player = Player("Test")
    hand = Hand(player)
    tile = Tile(TileSuit.MAN, 1)
    
    # 添加牌
    hand.add_tile(tile)
    assert len(hand.tiles) == 1
    
    # 移除牌
    hand.discard_tile(0)
    assert len(hand.tiles) == 0
    
    # 移除不存在的牌
    hand.discard_tile(0)  # 不应该抛出异常
    assert len(hand.tiles) == 0

def test_check_win():
    """测试和牌判定"""
    player = Player("Test")
    hand = Hand(player)
    
    # 测试七对子和牌
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2),
        Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 3),
        Tile(TileSuit.MAN, 4), Tile(TileSuit.MAN, 4),
        Tile(TileSuit.MAN, 5), Tile(TileSuit.MAN, 5),
        Tile(TileSuit.MAN, 6), Tile(TileSuit.MAN, 6),
        Tile(TileSuit.MAN, 7)
    ]
    
    for tile in tiles:
        hand.add_tile(tile)
        
    assert hand.check_win(Tile(TileSuit.MAN, 7))

def test_check_normal_win():
    """测试普通和牌型"""
    player = Player("Test")
    hand = Hand(player)
    
    # 添加一个基本和牌型(一杯口)
    tiles = [
        # 雀头
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        # 顺子1
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4),
        # 顺子2
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4),
        # 刻子
        Tile(TileSuit.PIN, 5), Tile(TileSuit.PIN, 5), Tile(TileSuit.PIN, 5),
        # 顺子3
        Tile(TileSuit.SOU, 7), Tile(TileSuit.SOU, 8)
    ]
    
    for tile in tiles:
        hand.add_tile(tile)
        
    # 测试和牌
    assert hand.check_win(Tile(TileSuit.SOU, 9))