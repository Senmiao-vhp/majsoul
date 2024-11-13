from typing import List
from src.core.tile import Tile


class Hand:
    def __init__(self):
        self.tiles = []
        self.melds = []  # 副露
        
    def add_tile(self, tile: Tile) -> None:
        """添加一张牌"""
        self.tiles.append(tile)
        
    def add_meld(self, tiles: List[Tile]) -> None:
        """添加一组副露"""
        self.melds.append(tiles)
        
    def remove_tile(self, tile: Tile) -> None:
        """移除一张牌"""
        if tile in self.tiles:
            self.tiles.remove(tile) 