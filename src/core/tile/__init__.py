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
        self._suit = suit
        self._value = value
        self._is_red = is_red  # 是否为赤牌
        self._hash = hash((suit, value, is_red))
        
    @property
    def suit(self):
        return self._suit
        
    @property
    def value(self):
        return self._value
        
    @property
    def is_red(self):
        return self._is_red
        
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
        return (self.suit == other.suit and 
                self.value == other.value and 
                self.is_red == other.is_red)
                
    def __hash__(self):
        return self._hash
        
    def __str__(self):
        base = f"{self.suit.value}{self.value}"
        return f"{base}红" if self.is_red else base
        
    def __lt__(self, other):
        if not isinstance(other, Tile):
            return NotImplemented
        # 先按花色排序，再按数值排序
        if self.suit != other.suit:
            return self.suit.value < other.suit.value
        return self.value < other.value