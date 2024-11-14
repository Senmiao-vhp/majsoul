from enum import Enum

class PlayerState(Enum):
    """玩家状态"""
    WAITING = "waiting"       # 等待
    THINKING = "thinking"     # 思考中
    WAITING_CHI = "waiting_chi"   # 等待吃
    WAITING_PON = "waiting_pon"   # 等待碰
    WAITING_KAN = "waiting_kan"   # 等待杠
    WAITING_RON = "waiting_ron"   # 等待荣和
    DEALING = "dealing"       # 发牌中
    DISCARDING = "discarding" # 出牌中
    WIN = "win"              # 胜利状态