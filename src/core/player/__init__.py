from typing import Optional
from ..hand import Hand
from ..tile import Tile
from .state import PlayerState

class Player:
    def __init__(self, name: str):
        """初始化玩家"""
        self.name = name
        self.hand = Hand()
        self.points = 0
        self.seat_wind = None  # 自风
        self.state = PlayerState.WAITING  # 添加状态属性
        
    def get_points(self) -> int:
        """获取玩家分数"""
        return self.points
        
    def set_points(self, points: int) -> None:
        """设置玩家分数"""
        self.points = points
        
    def add_points(self, points: int) -> None:
        """增加玩家分数"""
        self.points += points
        
    def take_action(self) -> None:
        """玩家行动"""
        pass 
        
    def draw_tile(self, tile: Tile) -> None:
        """摸牌"""
        self.hand.add_tile(tile)
        
    def discard_tile(self, index: int) -> Optional[Tile]:
        """打牌"""
        return self.hand.discard_tile(index)
        
    def set_state(self, new_state: PlayerState) -> None:
        """设置玩家状态"""
        self.state = new_state