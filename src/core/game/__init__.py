import json
from pathlib import Path
from typing import List, Dict, Any
from ..player import Player
from ..rules import Rules
from .state import GameState
from ..table import Table
from .controller import GameController

class Game:
    def __init__(self):
        self.table = Table()
        self.controller = GameController(self.table)
        self.rules = Rules()
        self.config: Dict[str, Any] = {}
        self._load_config()
        
    @property
    def players(self):
        """获取玩家列表"""
        return self.table.players
        
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
            # 清空现有玩家
            self.table.players.clear()
            
            # 创建玩家并设置初始分数
            initial_points = self.get_initial_points()
            for i in range(self.get_player_count()):
                player = Player(f"Player_{i+1}")
                player.set_points(initial_points)
                self.table.add_player(player)
            
            return True
        except Exception as e:
            print(f"游戏初始化失败: {e}")
            return False
        
    def start(self) -> bool:
        """开始游戏"""
        if not self.initialize():
            return False
        return self.controller.start_game()
        
    def update(self) -> None:
        """更新游戏状态"""
        if self.controller.state != GameState.PLAYING:
            return
            
        current_player = self.table.get_current_player()
        if current_player:
            self.controller.process_turn(current_player)
        
    def get_state(self) -> GameState:
        """获取当前游戏状态"""
        return self.controller.state
        
    def set_state(self, state: GameState) -> None:
        """设置游戏状态"""
        if not isinstance(state, GameState):
            raise ValueError("Invalid game state")
        self.controller.state = state