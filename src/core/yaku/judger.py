from typing import List, Optional, Dict
import logging
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.meld import Meld
from src.core.tile import Tile, TileSuit
from src.core.utils.logger import setup_logger

class YakuJudger:
    def __init__(self):
        self.calculator = HandCalculator()
        self.logger = setup_logger(__name__)
        # 添加役种名称映射
        self.yaku_name_mapping = {
            'Menzen Tsumo': 'tsumo',
            'Riichi': 'riichi',
            'Tanyao': 'tanyao',
            'Yakuhai (hatsu)': 'yakuhai_hatsu',
            'Chiitoitsu': 'chiitoitsu',
            'Honitsu': 'honitsu',
            'Pinfu': 'pinfu',
            'Aka Dora': 'aka_dora'
            # 可以继续添加其他役种的映射
        }

    def _get_suit_char(self, suit: TileSuit) -> str:
        """将TileSuit枚举转换为mahjong包使用的字符"""
        if suit == TileSuit.MAN:
            return 'm'
        elif suit == TileSuit.PIN:
            return 'p'
        elif suit == TileSuit.SOU:
            return 's'
        elif suit == TileSuit.HONOR:
            return 'z'
        return ''

    def judge(self, tiles: List[Tile], melds: Optional[List[List[Tile]]] = None, 
             win_tile: Optional[Tile] = None, is_tsumo: bool = False, 
             is_riichi: bool = False) -> Dict:
        """判断和牌役种
        
        Args:
            tiles: 手牌字符串
            melds: 副露列表
            win_tile: 和牌张
            is_tsumo: 是否自摸
            is_riichi: 是否立直
            
        Returns:
            Dict: 役种信息，包含 yaku(役种列表)、han(番数)、fu(符数)、score(点数)
        """
        try:
            self.logger.info(f"开始判定役种: 手牌数={len(tiles)}, 副露数={len(melds) if melds else 0}")
            
            # 1. 将手牌Tile对象转换为字符串格式
            man, pin, sou, honors = '', '', '', ''
            for tile in tiles:
                if tile.suit == TileSuit.MAN:
                    man += str(tile.value)
                elif tile.suit == TileSuit.PIN:
                    pin += str(tile.value)
                elif tile.suit == TileSuit.SOU:
                    sou += str(tile.value)
                elif tile.suit == TileSuit.HONOR:
                    honors += str(tile.value)
            
            # 2. 按照万筒索字的顺序转换手牌为136格式
            tiles_136 = []
            # 万子
            if man:
                tiles_136.extend(sorted(TilesConverter.string_to_136_array(man=man)))
            # 筒子
            if pin:
                tiles_136.extend(sorted(TilesConverter.string_to_136_array(pin=pin)))
            # 索子
            if sou:
                tiles_136.extend(sorted(TilesConverter.string_to_136_array(sou=sou)))
            # 字牌
            if honors:
                tiles_136.extend(sorted(TilesConverter.string_to_136_array(honors=honors)))
            
            # 3. 转换和牌张为136格式 (同样按照万筒索字的顺序)
            if win_tile:
                win_tile_136 = None
                if win_tile.suit == TileSuit.MAN:
                    win_tile_136 = TilesConverter.string_to_136_array(man=str(win_tile.value))[0]
                elif win_tile.suit == TileSuit.PIN:
                    win_tile_136 = TilesConverter.string_to_136_array(pin=str(win_tile.value))[0]
                elif win_tile.suit == TileSuit.SOU:
                    win_tile_136 = TilesConverter.string_to_136_array(sou=str(win_tile.value))[0]
                elif win_tile.suit == TileSuit.HONOR:
                    win_tile_136 = TilesConverter.string_to_136_array(honors=str(win_tile.value))[0]
            else:
                win_tile_136 = None
            
            # 4. 转换副露为Meld对象
            melds_136 = []
            if melds:
                for meld in melds:
                    # 将每个副露的牌转换为字符串格式
                    meld_man, meld_pin, meld_sou, meld_honors = '', '', '', ''
                    for tile in meld:
                        if tile.suit == TileSuit.MAN:
                            meld_man += str(tile.value)
                        elif tile.suit == TileSuit.PIN:
                            meld_pin += str(tile.value)
                        elif tile.suit == TileSuit.SOU:
                            meld_sou += str(tile.value)
                        elif tile.suit == TileSuit.HONOR:
                            meld_honors += str(tile.value)
                    
                    # 转换为136格式
                    meld_tiles = TilesConverter.string_to_136_array(
                        man=meld_man if meld_man else '',
                        pin=meld_pin if meld_pin else '',
                        sou=meld_sou if meld_sou else '',
                        honors=meld_honors if meld_honors else ''
                    )
                    
                    # 根据副露类型和牌的数量判断副露种类
                    if len(meld_tiles) == 3:
                        if len(set(meld_tiles)) == 1:  # 三张相同的牌
                            melds_136.append(Meld(meld_type=Meld.PON, tiles=meld_tiles))
                        else:  # 三张连续的牌
                            melds_136.append(Meld(meld_type=Meld.CHI, tiles=meld_tiles))
                    elif len(meld_tiles) == 4:  # 四张相同的牌
                        melds_136.append(Meld(meld_type=Meld.KAN, tiles=meld_tiles))
            
            # 5. 设置规则配置
            config = HandConfig(
                is_tsumo=is_tsumo,
                is_riichi=is_riichi,
                options=OptionalRules(
                    has_open_tanyao=True,  # 允许副露断幺
                    has_aka_dora=True,     # 允许赤宝牌
                )
            )
            
            # 6. 计算役种
            calculator = HandCalculator()
            result = calculator.estimate_hand_value(
                tiles=tiles_136,
                win_tile=win_tile_136,
                melds=melds_136,
                config=config
            )
            
            # 7. 返回结果时转换役种名称
            if result.yaku:  # 如果有役种（可以和牌）
                response = {
                    'yaku': [self.yaku_name_mapping.get(yaku.name, yaku.name) for yaku in result.yaku],
                    'han': result.han,
                    'fu': result.fu,
                    'score': result.cost['main'] if result.cost else 0  # 添加空值检查
                }
                self.logger.info(f"和牌判定结果: {response}")
                return response
            
            self.logger.info("未找到任何役种")
            return {
                'yaku': [],
                'han': 0,
                'fu': 0,
                'score': 0
            }
            
        except Exception as e:
            self.logger.error(f"役种判定出错: {str(e)}")
            self.logger.error("详细错误信息:", exc_info=True)
            return {
                'yaku': [],
                'han': 0,
                'fu': 0,
                'score': 0
            }