from typing import List, Optional
import random
from src.core.tile import Tile, TileSuit


class Wall:
    def __init__(self):
        self.tiles: List[Tile] = []
        self._remaining_count: int = 0
        self.initialize()
    
    def initialize(self) -> None:
        """初始化牌墙"""
        self.tiles.clear()
        # 生成所有牌
        for suit in [TileSuit.MAN, TileSuit.PIN, TileSuit.SOU]:
            for number in range(1, 10):
                for _ in range(4):
                    self.tiles.append(Tile(suit, number))
        
        # 生成字牌
        for number in range(1, 8):
            for _ in range(4):
                self.tiles.append(Tile(TileSuit.HONOR, number))
                
        self._remaining_count = len(self.tiles)
        self.shuffle()
    
    def shuffle(self) -> None:
        """洗牌"""
        random.shuffle(self.tiles)
    
    @property
    def remaining_count(self) -> int:
        """获取剩余牌数"""
        return self._remaining_count
    
    def draw(self) -> Optional[Tile]:
        """从牌山摸牌"""
        if not self.tiles or self._remaining_count <= 0:
            return None
        tile = self.tiles.pop()
        self._remaining_count -= 1
        return tile
    
    def get_remaining_count(self) -> int:
        """获取剩余牌数"""
        return self._remaining_count