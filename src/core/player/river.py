from typing import List
from src.core.tile import Tile

class River:
    """牌河类，记录玩家打出的牌"""
    def __init__(self):
        self.tiles: List[Tile] = []  # 存储打出的牌
        self.riichi_tile_index: int = -1  # 立直宣言牌的位置
        self.tsumogiri: List[bool] = []  # 记录是否为摸切(True/False)
        
    def add_tile(self, tile: Tile, is_tsumogiri: bool = False) -> None:
        """添加打出的牌到牌河
        
        Args:
            tile: 打出的牌
            is_tsumogiri: 是否为摸切
        """
        self.tiles.append(tile)
        self.tsumogiri.append(is_tsumogiri)
        
    def mark_riichi(self) -> None:
        """标记立直宣言牌"""
        self.riichi_tile_index = len(self.tiles) - 1
        
    def get_tiles(self) -> List[Tile]:
        """获取牌河中的所有牌"""
        return self.tiles.copy()
        
    def is_tsumogiri(self, index: int) -> bool:
        """判断指定位置的牌是否为摸切
        
        Args:
            index: 牌的位置
            
        Returns:
            bool: 是否为摸切
        """
        return self.tsumogiri[index]
        
    def clear(self) -> None:
        """清空牌河"""
        self.tiles.clear()
        self.tsumogiri.clear()
        self.riichi_tile_index = -1 