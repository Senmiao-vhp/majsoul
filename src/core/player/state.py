from enum import Enum, auto

class PlayerState(Enum):
    """玩家状态"""
    WAITING = auto()      # 等待
    THINKING = auto()     # 思考中
    WAITING_CHI = auto()  # 等待吃
    WAITING_PON = auto()  # 等待碰
    WAITING_KAN = auto()  # 等待杠
    WAITING_RON = auto()  # 等待荣和
    DEALING = auto()      # 发牌中
    DISCARDING = auto()   # 出牌中