from typing import List, Optional
from ..tile import Tile, TileSuit
from ..hand import Hand
from .state import PlayerState
from dataclasses import dataclass
from ..common.wind import Wind

@dataclass
class Player:
    """玩家类"""
    name: str
    seat_wind: Optional[Wind] = None
    is_furiten: bool = False
    
    def __init__(self, name: str):
        self.name = name
        self.hand = Hand()
        self.discards: List[Tile] = []
        self.state = PlayerState.WAITING
        self.is_riichi = False
        self.is_furiten = False
        self.points = 25000
        self.seat_wind = None
        self.selected_tile_index = -1  # 初始化为-1表示未选中
        
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
        if not isinstance(state, PlayerState):
            raise ValueError("Invalid player state")
        self.state = state
        
    def discard_tile(self, index: int) -> Optional[Tile]:
        """打出一张牌
        
        Args:
            index: 要打出的牌的索引
            
        Returns:
            打出的牌，如果失败返回None
        """
        if index < 0 or index >= len(self.hand.tiles):
            return None
        tile = self.hand.discard_tile(index)
        if tile:
            self.discards.append(tile)
        return tile
        
    def __hash__(self) -> int:
        """使 Player 可哈希，用于字典键"""
        return hash(self.name)  # 使用玩家名称作为哈希值
        
    def __eq__(self, other: object) -> bool:
        """比较两个玩家是否相等"""
        if not isinstance(other, Player):
            return NotImplemented
        return self.name == other.name
        
    def handle_tile_click(self, index: int) -> None:
        """处理牌的点击"""
        if 0 <= index < len(self.hand.tiles):
            self.selected_tile_index = index