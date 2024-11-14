from typing import List
from src.core.tile import Tile, TileSuit

class DoraManager:
    """宝牌管理器"""
    def __init__(self):
        self.dora_indicators: List[Tile] = []      # 表宝牌指示牌
        self.uradora_indicators: List[Tile] = []   # 里宝牌指示牌
        self.revealed_uradora = False              # 是否已翻开里宝牌
        
    def add_dora_indicator(self, tile: Tile):
        """添加表宝牌指示牌"""
        if len(self.dora_indicators) < 5:  # 最多5个指示牌
            self.dora_indicators.append(tile)
            
    def add_uradora_indicator(self, tile: Tile):
        """添加里宝牌指示牌"""
        if len(self.uradora_indicators) < 5:
            self.uradora_indicators.append(tile)
            
    def reveal_uradora(self):
        """翻开里宝牌"""
        self.revealed_uradora = True
        
    def get_dora_tiles(self) -> List[Tile]:
        """获取所有宝牌"""
        dora_tiles = []
        for indicator in self.dora_indicators:
            dora_tiles.append(self._get_next_tile(indicator))
        return dora_tiles
        
    def get_uradora_tiles(self) -> List[Tile]:
        """获取所有里宝牌"""
        if not self.revealed_uradora:
            return []
        uradora_tiles = []
        for indicator in self.uradora_indicators:
            uradora_tiles.append(self._get_next_tile(indicator))
        return uradora_tiles
        
    def _get_next_tile(self, tile: Tile) -> Tile:
        """获取下一张宝牌
        规则:
        - 数牌: 1->2->3...->9->1
        - 风牌: 东->南->西->北->东
        - 三元牌: 白->发->中->白
        """
        if tile.suit in [TileSuit.MAN, TileSuit.PIN, TileSuit.SOU]:
            next_value = tile.value % 9 + 1
            return Tile(tile.suit, next_value)
        elif tile.suit == TileSuit.HONOR:
            if 1 <= tile.value <= 4:
                return Tile(TileSuit.HONOR, 5)
            elif 5 <= tile.value <= 7:
                return Tile(TileSuit.HONOR, 8)
            else:
                return Tile(TileSuit.HONOR, 1) 