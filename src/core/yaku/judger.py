from typing import List, Optional, Dict
import logging
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.meld import Meld
from src.core.tile import Tile, TileSuit
from src.core.utils.logger import setup_logger
from src.core.utils.converter import TileConverter

class YakuJudger:
    def __init__(self):
        self.calculator = HandCalculator()
        self.logger = setup_logger(__name__)
        # 添加役种名称映射
        self.yaku_name_mapping = {
            '门清自摸': 'Menzen Tsumo',
            '立直': 'Riichi',
            '一发': 'Ippatsu',
            '断幺九': 'Tanyao',
            '平和': 'Pinfu',
            '一杯口': 'Iipeiko',
            '三色同顺': 'Sanshoku',
            '一气通贯': 'Ittsu',
            '混全带幺九': 'Chanta',
            '白': 'Yakuhai (haku)',
            '發': 'Yakuhai (hatsu)',
            '中': 'Yakuhai (chun)',
            '自风': 'Yakuhai (wind of place)',
            '场风': 'Yakuhai (wind of round)',
            '七对子': 'Chiitoitsu',
            '混一色': 'Honitsu',
            '清一色': 'Chinitsu',
            '对对和': 'Toitoi',
            '三暗刻': 'Sanankou',
            '三杠子': 'Sankantsu',
            '三色同刻': 'Sanshoku Douko',
            '四暗刻': 'Suuankou',
            '大三元': 'Daisangen',
            '字一色': 'tsuuiisou',
            '绿一色': 'Ryuuiisou',
            '清老头': 'Chinroutou',
            '国士无双': 'Kokushi',
            '小四喜': 'Shousuushii',
            '大四喜': 'Daisuushii',
            '天和': 'Tenhou',
            '地和': 'Chiihou',
            '人和': 'Renhou',
            '岭上开花': 'Rinshan Kaihou',
            '海底摸月': 'Haitei',
            '河底捞鱼': 'Houtei',
            '抢杠': 'Chankan',
            '双立直': 'Daburu Riichi',
            '宝牌': 'dora',
            '里宝牌': 'uradora',
            '赤宝牌': 'aka dora'
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
             uradora_tiles: List[Tile] = None, has_aka_dora: bool = False,
             is_ippatsu: bool = False,
             is_rinshan: bool = False,
             is_chankan: bool = False,
             is_haitei: bool = False,
             is_houtei: bool = False,
             is_daburu_riichi: bool = False,
             is_nagashi_mangan: bool = False,
             is_tenhou: bool = False,
             is_renhou: bool = False,
             is_chiihou: bool = False,
             is_open_riichi: bool = False,
             player_wind: Optional[int] = None,
             round_wind: Optional[int] = None,
             kyoutaku_number: int = 0,
             tsumi_number: int = 0,
             paarenchan: int = 0) -> Dict:
        """判定和牌役种

        Args:
            tiles (List[Tile]): 手牌列表
            melds (Optional[List[List[Tile]]], optional): 副露牌组列表. Defaults to None.
            win_tile (Optional[Tile], optional): 和牌张. Defaults to None.
            is_tsumo (bool, optional): 是否自摸. Defaults to False.
            is_riichi (bool, optional): 是否立直. Defaults to False.
            dora_tiles (List[Tile], optional): 表宝牌指示牌列表. Defaults to None.
            uradora_tiles (List[Tile], optional): 里宝牌指示牌列表. Defaults to None.
            has_aka_dora (bool, optional): 是否启用赤宝牌规则. Defaults to False.
            is_ippatsu (bool, optional): 是否一发. Defaults to False.
            is_rinshan (bool, optional): 是否岭上开花. Defaults to False.
            is_chankan (bool, optional): 是否抢杠. Defaults to False.
            is_haitei (bool, optional): 是否海底摸月. Defaults to False.
            is_houtei (bool, optional): 是否河底捞鱼. Defaults to False.
            is_daburu_riichi (bool, optional): 是否双立直. Defaults to False.
            is_nagashi_mangan (bool, optional): 是否流局满贯. Defaults to False.
            is_tenhou (bool, optional): 是否天和. Defaults to False.
            is_renhou (bool, optional): 是否人和. Defaults to False.
            is_chiihou (bool, optional): 是否地和. Defaults to False.
            is_open_riichi (bool, optional): 是否开立直. Defaults to False.
            player_wind (Optional[int], optional): 自风(0-3:东南西北). Defaults to None.
            round_wind (Optional[int], optional): 场风(0-3:东南西北). Defaults to None.
            kyoutaku_number (int, optional): 供托数. Defaults to 0.
            tsumi_number (int, optional): 积棒数. Defaults to 0.
            paarenchan (int, optional): 连庄数. Defaults to 0.

        Returns:
            Dict: 判定结果，包含:
                - yaku: 役种列表
                - han: 总番数
                - fu: 符数
                - score: 基本点数
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
                    if isinstance(meld, Meld):
                        melds_136.append(meld)  # 如果已经是Meld对象，直接添加
                    else:
                        # 如果是普通的牌列表，才需要转换
                        meld_136 = TileConverter.to_136_array(meld, has_aka_dora)
                        melds_136.append(Meld(
                            meld_type=self._get_meld_type(meld), 
                            tiles=meld_136,
                            opened=True
                        ))
            
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
                is_ippatsu=is_ippatsu,
                is_rinshan=is_rinshan,
                is_chankan=is_chankan,
                is_haitei=is_haitei,
                is_houtei=is_houtei,
                is_daburu_riichi=is_daburu_riichi,
                is_nagashi_mangan=is_nagashi_mangan,
                is_tenhou=is_tenhou,
                is_renhou=is_renhou,
                is_chiihou=is_chiihou,
                is_open_riichi=is_open_riichi,
                player_wind=player_wind,
                round_wind=round_wind,
                kyoutaku_number=kyoutaku_number,
                tsumi_number=tsumi_number,
                paarenchan=paarenchan,
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