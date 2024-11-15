from typing import List, Optional, Union
from ..tile import Tile, TileSuit
from ..hand import Hand
from .state import PlayerState
from dataclasses import dataclass
from ..common.wind import Wind
from src.core.player.furiten import FuritenState
from src.core.river import River

@dataclass
class Player:
    """玩家类"""
    name: str
    seat_wind: Optional[Wind] = None
    is_furiten: bool = False
    
    def __init__(self, name: str):
        self.name = name
        self.hand = Hand(self)
        self.discards: List[Tile] = []
        self.state = PlayerState.WAITING
        self.is_riichi = False
        self.is_furiten = False
        self.points = 25000
        self.seat_wind = None
        self.selected_tile_index = -1  # 初始化为-1表示未选中
        self.furiten = FuritenState()
        self.river = River()
        
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
        
    def discard_tile(self, tile_or_index: Union[Tile, int], is_tsumogiri: bool = False) -> Optional[Tile]:
        """打出一张牌
        
        Args:
            tile_or_index: 要打出的牌或其在手牌中的索引
            is_tsumogiri: 是否为摸切
            
        Returns:
            Optional[Tile]: 打出的牌，如果失败返回None
        """
        # 如果输入是索引，从手牌中获取对应的牌
        if isinstance(tile_or_index, int):
            if 0 <= tile_or_index < len(self.hand.tiles):
                tile = self.hand.tiles[tile_or_index]
            else:
                return None
        else:
            tile = tile_or_index
            
        # 从手牌中移除
        if self.hand.remove_tile(tile):
            # 添加到牌河
            self.river.add_tile(tile, is_tsumogiri)
            
            # 如果是立直状态且还未标记立直宣言牌
            if self.is_riichi and self.river.riichi_tile_index == -1:
                self.river.mark_riichi()
            
            # 添加到打牌记录
            self.discards.append(tile)
            self.furiten.current_turn_tiles.append(tile)
            
            # 检查振听
            if self.hand.waiting_tiles:
                self.furiten.check_furiten(self.hand.waiting_tiles, self.discards)
                
            return tile
            
        return None
        
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
        
    def add_discard(self, tile: Tile):
        """添加打出的牌"""
        self.discards.append(tile)
        self.furiten.current_turn_tiles.append(tile)
        
        # 检查振听
        if self.hand.waiting_tiles:
            self.furiten.check_furiten(self.hand.waiting_tiles, self.discards)
            
    def clear_turn(self):
        """清除当前巡状态"""
        self.furiten.clear_temporary_furiten()