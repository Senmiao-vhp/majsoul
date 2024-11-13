from enum import Enum
from typing import Optional

class TileSuit(Enum):
    """麻将牌的花色"""
    CHARACTERS = "万"  # 万子
    CIRCLES = "筒"     # 筒子
    BAMBOO = "条"      # 条子
    HONOR = "字"       # 字牌
    BONUS = "花"       # 花牌

class Tile:
    def __init__(self, suit: TileSuit, value: int, is_red: bool = False):
        self.suit = suit
        self.value = value
        self.is_red = is_red  # 是否为赤牌
        
    @property
    def is_valid(self) -> bool:
        """检查牌是否合法"""
        if self.suit in [TileSuit.CHARACTERS, TileSuit.CIRCLES, TileSuit.BAMBOO]:
            return 1 <= self.value <= 9
        elif self.suit == TileSuit.HONOR:
            return 1 <= self.value <= 7  # 东南西北白发中
        elif self.suit == TileSuit.BONUS:
            return 1 <= self.value <= 8  # 春夏秋冬梅兰竹菊
        return False
        
    def __eq__(self, other):
        if not isinstance(other, Tile):
            return False
        return self.suit == other.suit and self.value == other.value
        
    def __str__(self):
        return f"{self.suit}{self.value}" 