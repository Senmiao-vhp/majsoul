from enum import Enum, auto

class GameState(Enum):
    """游戏状态枚举"""
    WAITING = auto()      # 等待开始
    DEALING = auto()      # 发牌阶段
    PLAYING = auto()      # 游戏进行中
    FINISHED = auto()     # 游戏结束 