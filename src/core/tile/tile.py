from enum import Enum
from typing import Optional

class TileSuit(Enum):
    """牌的花色枚举"""
    MAN = "万"      # 万子
    PIN = "筒"      # 筒子
    SOU = "索"      # 索子
    HONOR = "字"    # 字牌

class Tile:
    def __init__(self, suit: TileSuit, value: int, is_red: bool = False):
        self._suit = suit
        self._value = value
        self._is_red = is_red
        self._hash = hash((suit, value, is_red))  # 预计算哈希值
        
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
        if not self._validate():
            return False
        return True
        
    def __eq__(self, other):
        if not isinstance(other, Tile):
            return False
        return (self.suit == other.suit and 
                self.value == other.value and 
                self.is_red == other.is_red)
                
    def __lt__(self, other):
        """实现小于比较，用于排序"""
        if not isinstance(other, Tile):
            return NotImplemented
        # 先按花色排序，再按数值排序
        if self.suit != other.suit:
            return self.suit.value < other.suit.value
        return self.value < other.value
                
    def __hash__(self):
        """实现哈希方法，使Tile可以作为字典键或集合元素"""
        return self._hash
                
    def __str__(self):
        base = f"{self.suit.value}{self.value}"
        return f"{base}红" if self.is_red else base
        
    def get_34_index(self) -> Optional[int]:
        """获取牌在34编码中的索引
        
        返回:
            int: 牌在34编码数组中的索引位置
            None: 如果是非法牌
            
        说明:
            - 万子(MAN): 0-8 (1-9)
            - 筒子(PIN): 9-17 (1-9)
            - 索子(SOU): 18-26 (1-9)
            - 字牌(HONOR): 27-33 (东南西北白发中)
        """
        if not self.is_valid:
            raise ValueError("Invalid tile cannot be converted to 34-array index")
            
        # 数牌: 0-26
        if self.suit == TileSuit.MAN:
            return self.value - 1
        elif self.suit == TileSuit.PIN:
            return self.value - 1 + 9
        elif self.suit == TileSuit.SOU:
            return self.value - 1 + 18
        # 字牌: 27-33 (东南西北白发中)
        elif self.suit == TileSuit.HONOR:
            if 1 <= self.value <= 7:
                return self.value - 1 + 27
                
        return None
        
    def _validate_aka_dora(self) -> bool:
        """验证赤宝牌的合法性"""
        if not self.is_red:
            return True
        # 赤宝牌只能是5万、5筒、5索
        return (self.value == 5 and 
                self.suit in [TileSuit.MAN, TileSuit.PIN, TileSuit.SOU])

    def _validate(self) -> bool:
        """验证牌的合法性"""
        # 首先验证基本的数值范围
        if self.suit in [TileSuit.MAN, TileSuit.PIN, TileSuit.SOU]:
            basic_valid = 1 <= self.value <= 9
        elif self.suit == TileSuit.HONOR:
            basic_valid = 1 <= self.value <= 7
        else:
            return False
        
        # 然后验证赤宝牌
        return basic_valid and self._validate_aka_dora()
        
    def is_terminal(self) -> bool:
        """判断是否为幺九牌
        
        Returns:
            bool: 是否为幺九牌
            
        说明:
            - 数牌(万、筒、索)的1和9
            - 所有字牌
        """
        # 数牌的1和9
        if self.suit in [TileSuit.MAN, TileSuit.PIN, TileSuit.SOU]:
            return self.value in [1, 9]
        # 字牌都算幺九牌
        elif self.suit == TileSuit.HONOR:
            return True
        return False