from dataclasses import dataclass
from typing import List, Optional
from src.core.tile import Tile

@dataclass
class FuritenState:
    """振听状态"""
    is_furiten: bool = False           # 是否振听
    is_riichi_furiten: bool = False    # 是否立直振听
    is_temporary_furiten: bool = False # 是否同巡振听
    current_turn_tiles: List[Tile] = None  # 当前巡打出的牌
    
    def __post_init__(self):
        if self.current_turn_tiles is None:
            self.current_turn_tiles = []
            
    def clear_temporary_furiten(self):
        """清除同巡振听"""
        self.is_temporary_furiten = False
        self.current_turn_tiles.clear()
        
    def check_furiten(self, waiting_tiles: List[Tile], discards: List[Tile]) -> bool:
        """检查振听状态
        Args:
            waiting_tiles: 听牌列表
            discards: 打出的牌列表
        """
        if not waiting_tiles:
            return False
            
        # 检查全局振听
        for tile in discards:
            if tile in waiting_tiles:
                self.is_furiten = True
                return True
                
        # 检查同巡振听
        for tile in self.current_turn_tiles:
            if tile in waiting_tiles:
                self.is_temporary_furiten = True
                return True
                
        return False 