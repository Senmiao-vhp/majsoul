from enum import Enum
from functools import total_ordering

class TileSuit(Enum):
    CHARACTERS = 1  # 万子
    CIRCLES = 2     # 筒子
    BAMBOO = 3      # 索子
    HONOR = 4       # 字牌

@total_ordering
class Tile:
    def __init__(self, suit: TileSuit, value: int):
        self._suit = suit
        self._value = value
        self._key = (suit, value)
        
    @property
    def suit(self):
        return self._suit
        
    @property
    def value(self):
        return self._value
    
    def __eq__(self, other):
        if not isinstance(other, Tile):
            return NotImplemented
        return self._key == other._key
        
    def __lt__(self, other):
        if not isinstance(other, Tile):
            return NotImplemented
        return (self.suit.value, self.value) < (other.suit.value, other.value)
        
    def __hash__(self):
        return hash(self._key)
        
    def __str__(self):
        return f"{self.suit.name}_{self.value}"
        
    def __repr__(self):
        return f"Tile({self.suit.name}, {self.value})"