from typing import List, Optional
from ..tile import Tile, TileSuit
import random

class Wall:
    """牌山类"""
    
    def __init__(self):
        self.tiles: List[Tile] = []
        self.dora_indicators: List[Tile] = []  # 宝牌指示牌
        self.dead_wall_size = 14  # 王牌区大小
        self._initialize_tiles()
        
    def _initialize_tiles(self) -> None:
        """初始化所有麻将牌"""
        # 生成数牌
        for suit in [TileSuit.CHARACTERS, TileSuit.CIRCLES, TileSuit.BAMBOO]:
            for value in range(1, 10):
                for _ in range(4):
                    self.tiles.append(Tile(suit, value))
                    
        # 生成字牌
        for value in range(1, 8):
            for _ in range(4):
                self.tiles.append(Tile(TileSuit.HONOR, value))
                
        self.shuffle()
        
    def shuffle(self) -> None:
        """洗牌"""
        random.shuffle(self.tiles)
        
    def draw(self) -> Optional[Tile]:
        """摸牌"""
        return self.tiles.pop() if self.tiles else None
        
    def get_remaining_count(self) -> int:
        """获取剩余牌数"""
        return len(self.tiles)
        
    def get_dora_indicators(self) -> List[Tile]:
        """获取宝牌指示牌"""
        return self.dora_indicators[:4]  # 最多显示4张宝牌指示牌