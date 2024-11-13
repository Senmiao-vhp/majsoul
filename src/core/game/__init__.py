import json
from pathlib import Path
from typing import List, Dict, Any
from ..player import Player
from ..rules import Rules

class Game:
    def __init__(self):
        self.players: List[Player] = []
        self.rules = Rules()
        self.config: Dict[str, Any] = {}
        self._load_config()
        
    def _load_config(self) -> None:
        """加载游戏配置"""
        try:
            config_path = Path(__file__).parent.parent.parent / 'assets' / 'config' / 'game.json'
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"加载游戏配置失败: {e}")
            # 使用默认配置
            self.config = {
                "version": "1.0.0",
                "player_count": 4,
                "initial_points": 25000
            }
            
    def get_player_count(self) -> int:
        """获取玩家数量"""
        return self.config.get("player_count", 4)
        
    def get_initial_points(self) -> int:
        """获取初始点数"""
        return self.config.get("initial_points", 25000)
        
    def get_version(self) -> str:
        """获取游戏版本"""
        return self.config.get("version", "1.0.0")
        
    def initialize(self) -> bool:
        """初始化游戏"""
        try:
            # 清空现有玩家列表
            self.players.clear()
            
            # 创建玩家并设置初始分数
            initial_points = self.get_initial_points()
            for i in range(self.get_player_count()):
                player = Player(f"Player_{i+1}")
                player.points = initial_points
                self.players.append(player)
            
            return True
        except Exception as e:
            print(f"游戏初始化失败: {e}")
            return False
        
    def start(self) -> bool:
        """开始游戏"""
        if not self.players:
            print("游戏未初始化")
            return False
            
        try:
            # 验证玩家数量
            if len(self.players) != self.get_player_count():
                print("玩家数量不正确")
                return False
                
            # 验证玩家初始分数
            initial_points = self.get_initial_points()
            for player in self.players:
                if player.points != initial_points:
                    print(f"玩家{player.name}分数不正确")
                    return False
            
            return True
        except Exception as e:
            print(f"游戏启动失败: {e}")
            return False
        
    def update(self) -> None:
        """更新游戏状态"""
        if not self.players:
            return
            
        try:
            # 让每个玩家执行行动
            for player in self.players:
                player.take_action()
        except Exception as e:
            print(f"游戏更新失败: {e}") 