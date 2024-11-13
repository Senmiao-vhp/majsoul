from enum import Enum, auto

class PlayerState(Enum):
    """玩家状态枚举"""
    WAITING = auto()    # 等待
    THINKING = auto()   # 思考中
    ACTING = auto()     # 行动中 