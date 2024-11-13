from typing import Optional

from src.core.player.state import PlayerState
from .state import GameState
from ..events import EventSystem
from ..player import Player
from ..table import Table
from ..wall import Wall

class GameController:
    def __init__(self, table: Table):
        """初始化游戏控制器"""
        self.table = table
        self.events = EventSystem()
        self.state = GameState.WAITING
        
    def start_game(self) -> bool:
        """开始游戏"""
        if len(self.table.players) != self.table.max_players:
            return False
            
        # 切换到发牌状态
        self.state = GameState.DEALING
        
        # 初始化牌墙
        self.table.initialize_wall()
        
        # 分配座位
        self.table.assign_seats()
        
        # 发牌
        if not self.table.deal_initial_tiles():
            return False
            
        # 保持在DEALING状态，等待外部切换到PLAYING
        return True
        
    def process_turn(self, player: Player) -> None:
        """处理玩家回合"""
        if self.state != GameState.PLAYING:
            return
            
        # 摸牌
        tile = self.table.wall.draw()
        if tile:
            player.hand.add_tile(tile)
            self.events.emit("tile_drawn", player, tile)
            
        # 等待玩家行动
        player.set_state(PlayerState.THINKING)
        
    def next_turn(self) -> Optional[Player]:
        """进入下一个回合"""
        return self.table.next_player()
        
    def end_game(self) -> None:
        """结束游戏"""
        self.state = GameState.FINISHED
        self.events.emit("game_ended") 