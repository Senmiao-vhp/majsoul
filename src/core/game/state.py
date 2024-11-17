from enum import IntEnum

class GameState(IntEnum):
    """游戏状态"""
    WAITING = 0     # 等待开始
    DEALING = 1     # 发牌中
    PLAYING = 2     # 游戏进行中
    FINISHED = 3    # 游戏结束

class ActionPriority(IntEnum):
    """操作优先级"""
    NONE = 0
    CHI = 1    # 吃
    PON = 2    # 碰
    KAN = 3    # 杠
    RON = 4    # 荣和
    TSUMO = 5  # 自摸