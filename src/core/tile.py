from enum import Enum
from functools import total_ordering
from typing import Optional
from .utils.logger import setup_logger

class TileSuit(Enum):
    """牌的花色枚举"""
    CHARACTERS = "万"  # 万子
    CIRCLES = "筒"     # 筒子
    BAMBOO = "索"      # 索子
    HONOR = "字"       # 字牌
    # BONUS = "花"     # 移除 BONUS，因为当前规则不需要花牌

@total_ordering
class Tile:
    def __init__(self, suit: TileSuit, value: int, is_red: bool = False):
        self.logger = setup_logger(__name__)
        self.suit = suit
        self.value = value
        self.is_red = is_red
        self.is_valid = self._validate()
        
    def _validate(self) -> bool:
        """验证牌的合法性"""
        if self.suit in [TileSuit.CHARACTERS, TileSuit.CIRCLES, TileSuit.BAMBOO]:
            return 1 <= self.value <= 9
        elif self.suit == TileSuit.HONOR:
            return 1 <= self.value <= 7
        return False
        
    def get_34_index(self) -> Optional[int]:
        """获取牌在34编码中的索引"""
        if not self.is_valid:
            raise ValueError("Invalid tile cannot be converted to 34-array index")
            
        if self.suit == TileSuit.CHARACTERS:
            return self.value - 1
        elif self.suit == TileSuit.CIRCLES:
            return self.value - 1 + 9
        elif self.suit == TileSuit.BAMBOO:
            return self.value - 1 + 18
        elif self.suit == TileSuit.HONOR:
            return self.value - 1 + 27
        return None