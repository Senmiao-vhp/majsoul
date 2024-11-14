import pytest
from src.core.hand import Hand
from src.core.player import Player
from src.core.tile import Tile, TileSuit
from src.core.yaku.judger import YakuJudger

def test_tanyao():
    """测试断幺九"""
    judger = YakuJudger()
    
    tiles = [
        # 2-8的牌
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2),  # 雀头
        Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4), Tile(TileSuit.MAN, 5),  # 顺子1
        Tile(TileSuit.SOU, 4), Tile(TileSuit.SOU, 5), Tile(TileSuit.SOU, 6),  # 顺子2
        Tile(TileSuit.PIN, 6), Tile(TileSuit.PIN, 7), Tile(TileSuit.PIN, 8),  # 等待8p的顺子
        Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 3)   # 刻子
    ]
    
    win_tile = Tile(TileSuit.PIN, 8)
    result = judger.judge(tiles=tiles, win_tile=win_tile, is_tsumo=True)
    
    assert result is not None
    assert "tanyao" in result["yaku"]
    assert result["han"] >= 1

def test_yakuhai():
    """测试役牌"""
    judger = YakuJudger()
    
    tiles = [
        # 包含发
        Tile(TileSuit.HONOR, 6), Tile(TileSuit.HONOR, 6), Tile(TileSuit.HONOR, 6),  # 发刻子
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4),  # 顺子1
        Tile(TileSuit.SOU, 5), Tile(TileSuit.SOU, 6), Tile(TileSuit.SOU, 7),  # 顺子2
        Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4), Tile(TileSuit.PIN, 5),  # 顺子3
        Tile(TileSuit.PIN, 9), Tile(TileSuit.PIN, 9)  # 雀头
    ]
    
    win_tile = Tile(TileSuit.PIN, 9)
    result = judger.judge(tiles, [], win_tile, True, False)
    assert "yakuhai_hatsu" in result["yaku"]
    assert result["han"] >= 1

def test_chitoitsu():
    """测试七对子"""
    judger = YakuJudger()
    
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 3),
        Tile(TileSuit.SOU, 5), Tile(TileSuit.SOU, 5),
        Tile(TileSuit.SOU, 7), Tile(TileSuit.SOU, 7),
        Tile(TileSuit.PIN, 9), Tile(TileSuit.PIN, 9),
        Tile(TileSuit.HONOR, 1), Tile(TileSuit.HONOR, 1),
        Tile(TileSuit.HONOR, 5), Tile(TileSuit.HONOR, 5)
    ]
    
    win_tile = Tile(TileSuit.HONOR, 5)
    result = judger.judge(tiles, [], win_tile, True, False)
    assert "chiitoitsu" in result["yaku"]
    assert result["han"] >= 2
    assert result["fu"] >= 25  # 七对子至少25符

def test_honitsu():
    """测试混一色"""
    judger = YakuJudger()
    
    tiles = [
        # 只使用万子和字牌
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 3), 
        Tile(TileSuit.MAN, 4),
        Tile(TileSuit.MAN, 5), Tile(TileSuit.MAN, 6), 
        Tile(TileSuit.MAN, 7),
        Tile(TileSuit.MAN, 7), Tile(TileSuit.MAN, 8), 
        Tile(TileSuit.MAN, 9),
        Tile(TileSuit.HONOR, 1), Tile(TileSuit.HONOR, 1), 
        Tile(TileSuit.HONOR, 1),
        Tile(TileSuit.HONOR, 5), Tile(TileSuit.HONOR, 5)
    ]
    
    win_tile = Tile(TileSuit.MAN, 2)
    result = judger.judge(tiles, [], win_tile, False, False)
    assert "honitsu" in result["yaku"]
    assert result["han"] >= 3  # 门清混一色3番

def test_pinfu():
    """测试平和"""
    judger = YakuJudger()
    
    tiles = [
        # 四组顺子加一对
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 2), 
        Tile(TileSuit.MAN, 3),
        Tile(TileSuit.SOU, 4), Tile(TileSuit.SOU, 5), 
        Tile(TileSuit.SOU, 6),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), 
        Tile(TileSuit.PIN, 4),
        Tile(TileSuit.PIN, 7), Tile(TileSuit.PIN, 8),
        Tile(TileSuit.PIN, 9),
        Tile(TileSuit.MAN, 5), Tile(TileSuit.MAN, 5)
    ]
    
    win_tile = Tile(TileSuit.MAN, 1)
    result = judger.judge(tiles, [], win_tile, True, False)
    assert "pinfu" in result["yaku"]
    assert result["han"] >= 1
    assert result["fu"] == 20  # 平和固定20符

def test_yaku_judge():
    """测试役种判定"""
    judger = YakuJudger()
    
    tiles = [
        # 刻子
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        # 顺子1
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4),
        # 顺子2
        Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4), Tile(TileSuit.PIN, 5),
        # 顺子3
        Tile(TileSuit.SOU, 5), Tile(TileSuit.SOU, 6), Tile(TileSuit.SOU, 7),
        # 雀头
        Tile(TileSuit.HONOR, 1), Tile(TileSuit.HONOR, 1)
    ]
    
    win_tile = Tile(TileSuit.MAN, 1)
    
    # 测试基本和牌判定
    result = judger.judge(tiles=tiles, win_tile=win_tile)
    assert result is not None
    
    # 测试自摸判定
    result = judger.judge(tiles=tiles, win_tile=win_tile, is_tsumo=True)
    assert result is not None
    assert 'tsumo' in result['yaku']
    
    # 测试立直判定
    result = judger.judge(tiles=tiles, win_tile=win_tile, is_riichi=True)
    assert result is not None
    assert 'riichi' in result['yaku']

def test_dora_calculation():
    """测试宝牌计算"""
    judger = YakuJudger()
    
    # 创建手牌
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),  # 雀头
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4),
        Tile(TileSuit.SOU, 2), Tile(TileSuit.SOU, 3), Tile(TileSuit.SOU, 4),
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2)  # 13张
    ]
    
    # 和牌张
    win_tile = Tile(TileSuit.MAN, 2)  # 和2m
    
    # 设置宝牌指示牌
    dora_indicators = [Tile(TileSuit.MAN, 1)]  # 指示牌1m，宝牌是2m
    uradora_indicators = [Tile(TileSuit.PIN, 1)]  # 指示牌1p，里宝牌是2p
    
    # 获取实际宝牌
    dora_tiles = [Tile(TileSuit.MAN, 2)]  # 2m
    uradora_tiles = [Tile(TileSuit.PIN, 2)]  # 2p
    
    # 测试普通和牌
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        dora_tiles=dora_tiles
    )
    assert result['han'] >= 1  # 应该有宝牌番数
    assert 'Dora' in result['yaku']  # 应该有1番宝牌
    
    # 测试立直和牌
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        is_riichi=True,
        dora_tiles=dora_tiles,
        uradora_tiles=uradora_tiles
    )
    assert result['han'] >= 2  # 应该有宝牌和里宝牌番数
    assert 'Dora' in result['yaku']  # 应该有1番宝牌
    #TODO assert 'UraDora' in result['yaku']  # 应该有1番里宝牌