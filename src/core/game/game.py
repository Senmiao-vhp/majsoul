import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..player import Player
from ..rules import Rules
from .state import GameState
from ..table import Table
from .controller import GameController
from .flow import GameFlow
from ..player.state import PlayerState
from ..events import EventEmitter
import os

class Game:
    def __init__(self):
        self.table = Table()
        self.controller = GameController(self.table)
        self.rules = Rules()
        self.config: Dict[str, Any] = {}
        self._load_config()
        self.flow = GameFlow(self)
        self.events = EventEmitter()
        
    @property
    def players(self):
        """获取玩家列表"""
        return self.table.players
        
    def _load_config(self) -> None:
        """加载游戏配置"""
        try:
            # 获取assets/config目录的路径
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                      'assets', 'config', 'rule.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"加载游戏配置失败: {e}")
            # 使用默认配置
            self.config = {
                "version": "1.0.0",
                "player_count": 4,
                "initial_points": 25000,
                "rules": {
                    "has_aka_dora": True,
                    "has_open_tanyao": True,
                    "has_double_yakuman": False
                }
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
            
            # 初始化牌山并发牌
            self.table.wall.initialize()
            for player in self.players:
                for _ in range(13):  # 每个玩家发13张牌
                    tile = self.table.wall.draw()
                    if tile:
                        player.hand.add_tile(tile)
            
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
        if current_player and current_player.state == PlayerState.WAITING:
            self.flow.start_turn(current_player)
        
    def get_state(self) -> GameState:
        """获取当前游戏状态"""
        return self.controller.state
        
    def set_state(self, state: GameState) -> None:
        """设置游戏状态"""
        if not isinstance(state, GameState):
            raise ValueError("Invalid game state")
        self.controller.state = state
        
    def skip_current_action(self) -> None:
        """跳过当前操作"""
        if self.controller.state != GameState.PLAYING:
            return
        
        if self.table and self.table.get_current_player():
            # 进入下一个玩家回合
            next_player = self.table.next_player()
            if next_player:
                self.controller.process_turn(next_player)
        
    def handle_tile_click(self, index: int) -> bool:
        """处理牌点击"""
        if self.get_state() != GameState.PLAYING:
            return False
        
        current_player = self.table.get_current_player()
        if current_player is None or current_player.state != PlayerState.THINKING:
            return False
        
        if 0 <= index < len(current_player.hand.tiles):
            current_player.selected_tile_index = index
            return True
        return False
        
    def get_current_player(self) -> Optional[Player]:
        return self.table.get_current_player()