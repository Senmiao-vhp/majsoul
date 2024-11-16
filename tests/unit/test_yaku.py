import pytest
from src.core.hand import Hand
from src.core.player import Player
from src.core.tile import Tile, TileSuit
from src.core.yaku.judger import YakuJudger
from src.core.utils.converter import TileConverter
from mahjong.meld import Meld
from mahjong.constants import EAST, SOUTH, WEST, NORTH

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
    assert "Tanyao" in result["yaku"]
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
    assert "Yakuhai (hatsu)" in result["yaku"]
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
    assert "Chiitoitsu" in result["yaku"]
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
    assert "Honitsu" in result["yaku"]
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
    assert "Pinfu" in result["yaku"]
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
    assert 'Menzen Tsumo' in result['yaku']
    
    # 测试立直判定
    result = judger.judge(tiles=tiles, win_tile=win_tile, is_riichi=True)
    assert result is not None
    assert 'Riichi' in result['yaku']

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
    dora_tiles = [Tile(TileSuit.MAN, 1)]  # 指示牌1m，宝牌是2m
    uradora_tiles = [Tile(TileSuit.PIN, 1)]  # 指示牌1p，里宝牌是2p
    
    
    # 测试普通和牌 门清三色两番，dora4番
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        dora_tiles=dora_tiles,
        uradora_tiles=uradora_tiles

    )
    assert result['han'] >= 6  # 应该有宝牌番数
    assert 'Dora' in result['yaku']  # 应该有4番宝牌
    
    # 测试立直和牌 门清三色两番，立直一番，dora4四番，uradora1一番，共8番
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        is_riichi=True,
        dora_tiles=dora_tiles,
        uradora_tiles=uradora_tiles
    )
    assert result['han'] >= 8  # 应该有宝牌和里宝牌番数
    assert 'Dora' in result['yaku']  # 应该有4番宝牌
    #TODO assert 'UraDora' in result['yaku']  # 应该有1番里宝牌

def test_aka_dora():
    """测试赤宝牌"""
    judger = YakuJudger()
    
    # 创建包含赤5万的手牌
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4),
        Tile(TileSuit.SOU, 2), Tile(TileSuit.SOU, 3), Tile(TileSuit.SOU, 4),
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2),
        Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4), 
        Tile(TileSuit.MAN, 5, True)  # 赤5万
    ]
    
    win_tile = Tile(TileSuit.MAN, 3)
    result = judger.judge(tiles=tiles, win_tile=win_tile, is_riichi=True, has_aka_dora=True)
    
    assert result is not None
    assert result['han'] >= 1  # 赤宝牌1番

def test_ippatsu():
    """测试一发"""
    judger = YakuJudger()
    
    # 基本和牌型
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4),
        Tile(TileSuit.SOU, 2), Tile(TileSuit.SOU, 3), Tile(TileSuit.SOU, 4),
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2),
        Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4), Tile(TileSuit.MAN, 5)
    ]
    
    win_tile = Tile(TileSuit.MAN, 5)
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        is_riichi=True,  # 一发必须在立直状态
        is_ippatsu=True
    )
    assert 'Ippatsu' in result['yaku']
    assert result['han'] >= 2  # 立直1番 + 一发1番

def test_rinshan():
    """测试岭上开花"""
    judger = YakuJudger()
    
    # 包含杠子的和牌型
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),        
        Tile(TileSuit.MAN, 6), Tile(TileSuit.MAN, 7), Tile(TileSuit.MAN, 8),
        Tile(TileSuit.MAN, 9), Tile(TileSuit.MAN, 9), Tile(TileSuit.MAN, 9),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 2),
        Tile(TileSuit.SOU, 3), Tile(TileSuit.SOU, 4), Tile(TileSuit.SOU, 5)
    ]
    
    # 创建明杠
    kan_tiles = [
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 2), 
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 2)
    ]
    
    # 设置明杠
    kan_meld = Meld(
        meld_type=Meld.KAN,
        tiles=TileConverter.to_136_array(kan_tiles),
        opened=True,  # 明杠       
    )

    win_tile = Tile(TileSuit.MAN, 1)  # 岭上开花的和牌
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        melds=[kan_meld],  # 传入杠子
        is_rinshan=True,
        is_tsumo=True  # 岭上开花必须自摸
    )
    
    assert 'Rinshan Kaihou' in result['yaku']
    assert result['han'] >= 1

def test_tenhou():
    """测试天和"""
    judger = YakuJudger()
    
    # 庄家起手和牌型
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4),
        Tile(TileSuit.SOU, 5), Tile(TileSuit.SOU, 5), Tile(TileSuit.SOU, 5),
        Tile(TileSuit.HONOR, 1), Tile(TileSuit.HONOR, 1), Tile(TileSuit.HONOR, 1),
        Tile(TileSuit.MAN, 9), Tile(TileSuit.MAN, 9)
    ]
    
    win_tile = Tile(TileSuit.MAN, 9)
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        is_tenhou=True,
        is_tsumo=True  # 天和必须自摸
    )
    assert 'Tenhou' in result['yaku']
    assert result['han'] >= 13  # 天和役满

def test_chankan():
    """测试抢杠"""
    judger = YakuJudger()
    
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4),
        Tile(TileSuit.SOU, 2), Tile(TileSuit.SOU, 3), Tile(TileSuit.SOU, 4),
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2),
        Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4), Tile(TileSuit.MAN, 5)  
    ]
    
    win_tile = Tile(TileSuit.MAN, 2)  # 抢杠的牌
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        is_chankan=True
    )
    assert 'Chankan' in result['yaku']
    assert result['han'] >= 1

def test_haitei():
    """测试海底摸月"""
    judger = YakuJudger()
    
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4),
        Tile(TileSuit.SOU, 2), Tile(TileSuit.SOU, 3), Tile(TileSuit.SOU, 4),
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2),
        Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4), Tile(TileSuit.MAN, 5)
    ]
    
    win_tile = Tile(TileSuit.MAN, 4)
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        is_haitei=True,
        is_tsumo=True  # 海底摸月必须自摸
    )
    assert 'Haitei Raoyue' in result['yaku']
    assert result['han'] >= 1

def test_houtei():
    """测试河底捞鱼"""
    judger = YakuJudger()
    
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4),
        Tile(TileSuit.SOU, 2), Tile(TileSuit.SOU, 3), Tile(TileSuit.SOU, 4),
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2),
        Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4), Tile(TileSuit.MAN, 5)
    ]
    
    win_tile = Tile(TileSuit.MAN, 4)
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        is_houtei=True,
        is_tsumo=False  # 河底捞鱼必须荣和
    )
    assert 'Houtei Raoyui' in result['yaku']
    assert result['han'] >= 1

def test_chiihou():
    """测试地和"""
    judger = YakuJudger()
    
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4),
        Tile(TileSuit.SOU, 5), Tile(TileSuit.SOU, 5), Tile(TileSuit.SOU, 5),
        Tile(TileSuit.HONOR, 1), Tile(TileSuit.HONOR, 1), Tile(TileSuit.HONOR, 1),
        Tile(TileSuit.MAN, 9), Tile(TileSuit.MAN, 9)
    ]
    
    win_tile = Tile(TileSuit.MAN, 9)
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        is_chiihou=True,
        is_tsumo=True  # 地和必须自摸
    )
    assert 'Chiihou' in result['yaku']
    assert result['han'] >= 13  # 地和役满

def test_daburu_riichi():
    """测试双立直"""
    judger = YakuJudger()
    
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4),
        Tile(TileSuit.SOU, 2), Tile(TileSuit.SOU, 3), Tile(TileSuit.SOU, 4),
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2),
        Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4), Tile(TileSuit.MAN, 5)
    ]
    
    win_tile = Tile(TileSuit.MAN, 5)
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        is_daburu_riichi=True,  # 双立直
        is_riichi=True  # 双立直同时也是立直
    )
    assert 'Double Riichi' in result['yaku']
    assert result['han'] >= 2  # 双立直2番

#TODO 流局满贯测试
# def test_nagashi_mangan():
#     """测试流局满贯"""
    

def test_renhou():
    """测试人和"""
    judger = YakuJudger()
    
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4),
        Tile(TileSuit.SOU, 2), Tile(TileSuit.SOU, 3), Tile(TileSuit.SOU, 4),
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2),
        Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4), Tile(TileSuit.MAN, 5)
    ]
    
    win_tile = Tile(TileSuit.MAN, 5)
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        is_renhou=True
    )
    assert 'Renhou' in result['yaku']
    assert result['han'] >= 1

def test_open_riichi():
    """测试开立直"""
    judger = YakuJudger()
    
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4),
        Tile(TileSuit.SOU, 2), Tile(TileSuit.SOU, 3), Tile(TileSuit.SOU, 4),
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2),
        Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4), Tile(TileSuit.MAN, 5)
    ]
    
    win_tile = Tile(TileSuit.MAN, 5)
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        is_open_riichi=True,
        is_riichi=True  # 开立直同时也是立直
    )
    assert 'Open Riichi' in result['yaku']
    assert result['han'] >= 1

def test_wind_yaku():
    """测试自风场风役"""
    judger = YakuJudger()
    
    # 包含东风刻子和南风刻子的手牌
    tiles = [
        Tile(TileSuit.HONOR, 1), Tile(TileSuit.HONOR, 1), Tile(TileSuit.HONOR, 1),  # 东风刻子
        Tile(TileSuit.HONOR, 2), Tile(TileSuit.HONOR, 2), Tile(TileSuit.HONOR, 2),  # 南风刻子
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4),
        Tile(TileSuit.SOU, 9), Tile(TileSuit.SOU, 9)  # 雀头
    ]
    
    win_tile = Tile(TileSuit.SOU, 9)
    result = judger.judge(
        tiles=tiles,
        win_tile=win_tile,
        player_wind=EAST,  # 东家(0-3:东南西北)
        round_wind=SOUTH    # 南场
    )
    
    assert 'Yakuhai (wind of place)' in result['yaku']  # 自风(东)
    assert 'Yakuhai (wind of round)' in result['yaku']  # 场风(南)
    assert result['han'] >= 2  # 自风1番 + 场风1番