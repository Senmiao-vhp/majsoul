from typing import List, Optional
from src.core.tile import Tile, TileSuit

class Hand:
    def __init__(self):
        self.tiles: List[Tile] = []  # 手牌列表
        self.melds: List[List[Tile]] = []  # 副露列表
        self.waiting_tiles: List[Tile] = []  # 听牌列表
        
    def add_tile(self, tile: Tile) -> None:
        """添加一张牌到手牌"""
        self.tiles.append(tile)
        self._sort_tiles()  # 保持手牌有序
        
    def discard_tile(self, index: int) -> Optional[Tile]:
        """打出一张手牌
        Args:
            index: 要打出的牌的索引
        Returns:
            打出的牌,如果索引无效则返回None
        """
        if 0 <= index < len(self.tiles):
            return self.tiles.pop(index)
        return None
        
    def add_meld(self, tiles: List[Tile]) -> None:
        """添加一组副露
        Args:
            tiles: 要添加的副露牌组
        """
        self.melds.append(tiles)
        
    def _sort_tiles(self) -> None:
        """对手牌进行排序"""
        self.tiles.sort(key=lambda x: (x.suit.value, x.value)) 