from enum import Enum
from typing import List, Optional, Dict
from ..player import Player
from ..hand import Hand
from ..wall import Wall
from ..tile import Tile

class Wind(Enum):
    """座位方位"""
    EAST = "东"
    SOUTH = "南"
    WEST = "西"
    NORTH = "北"

class Table:
    def __init__(self, player_count: int = 4):
        self.players: List[Player] = []
        self.current_player_index: int = 0
        self.dealer_index: int = 0
        self.round: int = 1
        self.max_players = player_count
        self.wind_assignments: Dict[Player, Wind] = {}
        self.initialize_wall()
        
    def add_player(self, player: Player) -> bool:
        """添加玩家到牌桌"""
        if len(self.players) >= self.max_players:
            return False
        self.players.append(player)
        return True
        
    def assign_seats(self) -> None:
        """分配座位"""
        winds = list(Wind)
        self.wind_assignments.clear()
        for i, player in enumerate(self.players):
            if i < len(winds):
                self.wind_assignments[player] = winds[i]
                player.seat_wind = winds[i]
                
    def get_player_wind(self, player: Player) -> Optional[Wind]:
        """获取玩家的座位方位"""
        return self.wind_assignments.get(player)
        
    def rotate_dealer(self) -> None:
        """轮换庄家"""
        self.dealer_index = (self.dealer_index + 1) % len(self.players)
        self.current_player_index = self.dealer_index
        
    def get_dealer(self) -> Optional[Player]:
        """获取庄家"""
        if not self.players:
            return None
        return self.players[self.dealer_index]
        
    def get_current_player(self) -> Optional[Player]:
        """获取当前玩家"""
        if not self.players:
            return None
        return self.players[self.current_player_index]
        
    def next_player(self) -> Optional[Player]:
        """切换到下一个玩家"""
        if not self.players:
            return None
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return self.get_current_player()

    def start_round(self) -> bool:
        """开始新的一轮"""
        if len(self.players) != 4:
            return False
            
        self.round += 1
        self.current_player_index = self.dealer_index
        self.initialize_wall()
        
        # 发牌
        return self.deal_initial_tiles()

    def reset_round(self) -> None:
        """重置当前轮"""
        self.current_player_index = self.dealer_index
        for player in self.players:
            player.hand = Hand()

    def rotate_winds(self) -> None:
        """轮转座位方位"""
        if len(self.players) != self.max_players:
            return
        
        # 保存当前风位
        winds = list(Wind)
        old_assignments = self.wind_assignments.copy()
        
        # 轮转风位
        self.wind_assignments.clear()
        for player in self.players:
            old_wind = old_assignments[player]
            new_wind_index = (winds.index(old_wind) + 1) % len(winds)
            self.wind_assignments[player] = winds[new_wind_index]
            player.seat_wind = winds[new_wind_index]

    def initialize_wall(self) -> None:
        """初始化牌墙"""
        self.wall = Wall()
        self.wall.shuffle()
        
    def deal_initial_tiles(self) -> bool:
        """发初始手牌"""
        if len(self.players) != self.max_players:
            return False
        
        # 每个玩家发13张牌
        for _ in range(13):
            for player in self.players:
                tile = self.wall.draw()
                if tile:
                    player.hand.add_tile(tile)
                else:
                    return False
                
        return True
