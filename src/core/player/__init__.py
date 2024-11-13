class Player:
    def __init__(self, name: str):
        """初始化玩家"""
        self.name = name
        self.hand = []
        self.points = 0
        
    def get_points(self) -> int:
        """获取玩家分数"""
        return self.points
        
    def set_points(self, points: int) -> None:
        """设置玩家分数"""
        self.points = points
        
    def add_points(self, points: int) -> None:
        """增加玩家分数"""
        self.points += points
        
    def take_action(self):
        """玩家行动"""
        pass 