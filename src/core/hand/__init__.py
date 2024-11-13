from typing import List, Optional
from ..tile import Tile

class Hand:
    def __init__(self):
        """初始化手牌"""
        self.tiles: List[Tile] = []
        self.melds: List[List[Tile]] = []  # 副露
        
    def add_tile(self, tile: Tile) -> None:
        """添加一张牌"""
        self.tiles.append(tile)
        self._sort_tiles()
        
    def discard_tile(self, index: int) -> Optional[Tile]:
        """打出一张牌"""
        if 0 <= index < len(self.tiles):
            return self.tiles.pop(index)
        return None
        
    def _sort_tiles(self) -> None:
        """整理手牌"""
        self.tiles.sort(key=lambda x: (x.suit.value, x.value))
        
    def add_meld(self, tiles: List[Tile]) -> None:
        """添加一组副露"""
        if len(tiles) >= 3:  # 副露至少需要3张牌
            self.melds.append(tiles)
            self._sort_tiles()
        
    def get_melds(self) -> List[List[Tile]]:
        """获取所有副露"""
        return self.melds