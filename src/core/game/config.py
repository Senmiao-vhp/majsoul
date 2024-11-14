class GameConfig:
    """游戏配置类"""
    def __init__(self):
        self.dora_count = 1      # 初始宝牌指示牌数量
        self.aka_dora = True     # 是否启用赤宝牌
        self.uradora = False     # 是否启用里宝牌
        self.open_tanyao = True  # 是否允许副露断幺 
        self.dead_wall_count = 14  # 王牌数（14张）