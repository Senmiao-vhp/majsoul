from typing import List, Optional, Dict
import logging
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.meld import Meld
from src.core.tile import Tile, TileSuit
from src.core.utils.logger import setup_logger
from src.core.converter import TileConverter

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
             is_riichi: bool = False, dora_tiles: List[Tile] = None, 
             uradora_tiles: List[Tile] = None, has_aka_dora: bool = False) -> Dict:
        """判断和牌役种
        
        Args:
            tiles: 手牌字符串
            melds: 副露列表
            win_tile: 和牌张
            is_tsumo: 是否自摸
            is_riichi: 是否立直
            dora_tiles: 表宝牌指示牌列表
            uradora_tiles: 里宝牌指示牌列表
            has_aka_dora: 是否包含赤宝牌

        Returns:
            Dict: 役种信息，包含 yaku(役种列表)、han(番数)、fu(符数)、score(点数)
        """
        try:
            self.logger.info(f"开始判定役种: 手牌数={len(tiles)}, 副露数={len(melds) if melds else 0}")
            self.logger.debug(f"手牌详情: {[str(t) for t in tiles]}")
            
            # 转换手牌为136格式
            tiles_136 = TileConverter.to_136_array(tiles, has_aka_dora)
            
            # 转换和牌为136格式
            win_tile_136 = None
            if win_tile:
                win_tile_136 = TileConverter.to_136_array([win_tile], has_aka_dora)[0]
            
            # 转换副露为136格式
            melds_136 = []
            if melds:
                for meld in melds:
                    meld_136 = TileConverter.to_136_array(meld, has_aka_dora)
                    melds_136.append(Meld(mel_type=self._get_meld_type(meld), tiles=meld_136))
            
            # 转换宝牌指示牌为136格式
            dora_136 = []
            if dora_tiles:
                dora_136 = TileConverter.to_136_array(dora_tiles)
            
            # 转换里宝牌指示牌为136格式
            uradora_136 = []
            if is_riichi and uradora_tiles:
                uradora_136 = TileConverter.to_136_array(uradora_tiles, has_aka_dora)
            
            # 设置规则配置
            config = HandConfig(
                is_tsumo=is_tsumo,
                is_riichi=is_riichi,
                is_ippatsu=False,           # 是否一发
                is_rinshan=False,           # 是否岭上开花
                is_chankan=False,           # 是否抢杠
                is_haitei=False,           # 是否海底摸月
                is_houtei=False,           # 是否河底捞鱼
                is_daburu_riichi=False,    # 是否双立直
                is_nagashi_mangan=False,   # 是否流局满贯
                is_tenhou=False,           # 是否天和
                is_renhou=False,           # 是否人和
                is_chiihou=False,          # 是否地和
                is_open_riichi=False,      # 是否开立直
                player_wind=None,          # 自风
                round_wind=None,           # 场风
                kyoutaku_number=0,         # 供托数
                tsumi_number=0,           # 积棒数
                paarenchan=0,             # 连庄数
                options=OptionalRules(
                    has_open_tanyao=True,
                    has_aka_dora=has_aka_dora,
                    has_double_yakuman=False,  # 不使用双倍役满
                    kazoe_limit=None,          # 不限制累计役满
                ),
                
            )
            
            # 添加宝牌指示牌
            dora_indicators = []
            if dora_136:
                dora_indicators.extend(dora_136)
            if is_riichi and uradora_136:
                dora_indicators.extend(uradora_136)
            self.logger.info(f"宝牌指示牌: {dora_indicators}")
            
            # 计算役种
            result = self.calculator.estimate_hand_value(
                tiles=tiles_136,
                win_tile=win_tile_136,
                melds=melds_136,
                config=config,
                dora_indicators=dora_indicators if dora_indicators else None
                
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

    def _get_meld_type(self, meld: List[Tile]) -> str:
        """根据副露类型和牌的数量判断副露种类"""
        if len(meld) == 3:
            if len(set(meld)) == 1:  # 三张相同的牌
                return Meld.PON
            else:  # 三张连续的牌
                return Meld.CHI
        elif len(meld) == 4:  # 四张相同的牌
            return Meld.KAN