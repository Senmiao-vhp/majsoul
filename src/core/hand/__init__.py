from typing import List, Optional, Union, Dict
from collections import Counter
from ..tile import Tile, TileSuit
from mahjong.shanten import Shanten
from ..utils.logger import setup_logger
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.meld import Meld
from src.core.yaku.judger import YakuJudger
import logging

class Hand:
    def __init__(self, player=None):
        """初始化手牌"""
        self.tiles: List[Tile] = []
        self.melds: List[List[Tile]] = []  # 副露
        self.waiting_tiles: List[Tile] = []  # 听牌列表
        self.shanten = Shanten()
        self.player = player
        self.logger = logging.getLogger(__name__)
        
    def add_tile(self, tile: Tile) -> None:
        """添加一张牌"""
        self.tiles.append(tile)
        self._sort_tiles()
        
    def discard_tile(self, tile_or_index: Union[Tile, int]) -> Optional[Tile]:
        """打出一张牌"""
        if isinstance(tile_or_index, int):
            if 0 <= tile_or_index < len(self.tiles):
                return self.tiles.pop(tile_or_index)
        elif isinstance(tile_or_index, Tile):
            if tile_or_index in self.tiles:
                self.tiles.remove(tile_or_index)
                return tile_or_index
        return None
        
    def _sort_tiles(self) -> None:
        """整理手牌"""
        self.tiles.sort(key=lambda x: (x.suit.value, x.value))
        
    def add_meld(self, tiles: List[Tile]) -> None:
        """添加一组副露"""
        if len(tiles) >= 3:  # 副露至少需要3张牌
            self.melds.append(tiles)
            
    def remove_tile(self, tile: Tile) -> bool:
        """从手牌中移除一张牌
        
        Args:
            tile: 要移除的牌
            
        Returns:
            bool: 是否移除成功
        """
        if tile in self.tiles:
            self.tiles.remove(tile)
            return True
        return False
        
    def check_win(self, tile: Optional[Tile] = None) -> bool:
        """检查是否和牌"""
        test_tiles = self.tiles.copy()
        if tile:
            test_tiles.append(tile)
            
        # 检查普通和牌型
        if len(test_tiles) == 14:
            tiles_34 = self._convert_tiles_to_34_array(test_tiles)
            return self.shanten.calculate_shanten(tiles_34) == -1
                
        return False
        
    def _convert_tiles_to_34_array(self, tiles: List[Tile]) -> List[int]:
        """将手牌转换为34编码数组"""
        array = [0] * 34
        for tile in tiles:
            index = tile.get_34_index()
            if index is not None:
                array[index] += 1
        return array
        
    def check_tenpai(self) -> List[Tile]:
        """检查听牌，返回能让手牌听牌的进张"""
        waiting_tiles = []
        self.logger.debug("开始检查听牌")
        self.logger.debug(f"当前手牌: {[str(t) for t in self.tiles]}")
        
        # 转换手牌格式
        tiles_34 = self._convert_tiles_to_34_array(self.tiles)
        self.logger.debug(f"转换后的34数组: {tiles_34}")
        
        # 计算当前向听数
        current_shanten = self.shanten.calculate_shanten(tiles_34)
        self.logger.debug(f"当前向听数: {current_shanten}")
        
        # 如果已经和牌或向听数大于1，则不是听牌状态
        if current_shanten < 0 or current_shanten > 1:
            self.logger.debug(f"非听牌状态，当前向听数: {current_shanten}")
            return []
        
        # 检查所有可能的牌
        for suit in TileSuit:
            max_value = 7 if suit == TileSuit.HONOR else 9
            for value in range(1, max_value + 1):
                test_tile = Tile(suit, value)
                if not test_tile.is_valid:
                    continue
                    
                # 复制当前手牌并添加测试牌
                test_tiles = self.tiles.copy()
                test_tiles.append(test_tile)
                test_tiles_34 = self._convert_tiles_to_34_array(test_tiles)
                test_shanten = self.shanten.calculate_shanten(test_tiles_34)
                
                # 如果当前是一向听，则找能让向听数变为0的牌
                # 如果当前是听牌，则找能让向听数变为-1的牌
                if test_shanten < current_shanten:
                    self.logger.debug(f"找到有效进张: {test_tile}")
                    waiting_tiles.append(test_tile)
        
        self.logger.debug(f"听牌检查完成，进张数: {len(waiting_tiles)}")
        return waiting_tiles
    

    def check_yaku(self, win_tile: Tile, is_tsumo: bool = False) -> Dict:
        """检查和牌役种
        
        Args:
            win_tile: 和牌
            is_tsumo: 是否自摸
            
        Returns:
            Dict: 役种列表，如果没有役种返回空字典
        """
        judger = YakuJudger()
        result = judger.judge(
            tiles=self.tiles,
            melds=self.melds,
            win_tile=win_tile,
            is_tsumo=is_tsumo,
            is_riichi=self.player.is_riichi if self.player else False,
            dora_tiles=self.player.game.table.wall.dora_manager.get_dora_tiles() if self.player and self.player.game else None,
            uradora_tiles=self.player.game.table.wall.dora_manager.get_uradora_tiles() if self.player and self.player.game else None
        )
        return result if result is not None else {}  # 如果没有役种返回空字典