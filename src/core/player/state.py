from enum import IntEnum

class PlayerState(IntEnum):
    """玩家状态"""
    WAITING = 0         # 等待
    THINKING = 1        # 思考中
    DISCARDING = 2      # 出牌中
    WAITING_CHI = 3     # 等待吃
    WAITING_PON = 4     # 等待碰
    WAITING_KAN = 5     # 等待杠
    WAITING_RON = 6     # 等待荣和
    WIN = 7            # 和牌