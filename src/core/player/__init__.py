from typing import List, Optional
from ..tile import Tile, TileSuit
from ..hand import Hand
from .state import PlayerState

class Player:
    """玩家类"""
    
    def __init__(self, name: str):
        self.name = name
        self.hand = Hand()
        self.points = 0
        self.state = PlayerState.WAITING
        self.discards: List[Tile] = []  # 存储打出的牌
        self.is_riichi = False  # 是否立直
        
    def set_points(self, points: int) -> None:
        """设置分数"""
        self.points = points
        
    def get_points(self) -> int:
        """获取分数"""
        return self.points
        
    def add_points(self, points: int) -> None:
        """增加分数"""
        self.points += points
        
    def set_state(self, state: PlayerState) -> None:
        """设置玩家状态"""
        self.state = state
        
    def discard_tile(self, index: int) -> Optional[Tile]:
        """打出一张牌
        
        Args:
            index: 要打出的牌的索引
            
        Returns:
            打出的牌，如果失败返回None
        """
        tile = self.hand.discard_tile(index)
        if tile:
            self.discards.append(tile)
        return tile