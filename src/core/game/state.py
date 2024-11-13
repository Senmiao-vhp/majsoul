from enum import Enum, auto

class GameState(Enum):
    """游戏状态"""
    WAITING = auto()    # 等待开始
    DEALING = auto()    # 发牌中
    PLAYING = auto()    # 游戏进行中
    FINISHED = auto()   # 游戏结束

class ActionPriority(Enum):
    """操作优先级"""
    NONE = 0
    CHI = 1    # 吃
    PON = 2    # 碰
    KAN = 3    # 杠
    RON = 4    # 荣和
    TSUMO = 5  # 自摸