from typing import List, Optional, Dict
from ..common.wind import Wind
from ..player import Player
from ..hand import Hand
from ..wall import Wall
from ..tile import Tile

class Table:
    def __init__(self, player_count: int = 4):
        self.players: List[Player] = []
        self.current_player_index: int = 0
        self.dealer_index: int = 0
        self.round: int = 1
        self.max_players = player_count
        self.wind_assignments: Dict[str, Wind] = {}
        self.wall: Optional[Wall] = None
        self.round_wind: int = 0  # 0=东, 1=南, 2=西, 3=北
        self.initialize_wall()
        
    def add_player(self, player: Player) -> bool:
        """添加玩家"""
        if len(self.players) >= self.max_players:
            return False
        
        self.players.append(player)
        # 设置玩家风位
        player.seat_wind = Wind(27 + len(self.players) - 1)  # 东南西北依次分配
        return True
        
    def assign_seats(self) -> None:
        """分配座位"""
        winds = [Wind.EAST, Wind.SOUTH, Wind.WEST, Wind.NORTH]
        for player, wind in zip(self.players, winds):
            player.seat_wind = wind
            self.wind_assignments[player.name] = wind
        
    def get_player_wind(self, player: Player) -> Optional[Wind]:
        """获取玩家的风位"""
        return self.wind_assignments.get(player.name)
        
    def rotate_dealer(self) -> None:
        """轮换庄家"""
        self.dealer_index = (self.dealer_index + 1) % len(self.players)
        self.current_player_index = self.dealer_index
        
    @property
    def dealer(self) -> Optional[Player]:
        """获取当前庄家"""
        if not self.players:
            return None
        return self.players[self.dealer_index]
    
    @dealer.setter
    def dealer(self, player: Player):
        """设置庄家
        Args:
            player: 要设置为庄家的玩家
        """
        if player in self.players:
            self.dealer_index = self.players.index(player)
        
    def get_current_player(self) -> Optional[Player]:
        """获取当前玩家"""
        if not self.players or len(self.players) < self.max_players:
            return None
        if self.current_player_index >= len(self.players):
            return None
        return self.players[self.current_player_index]
        
    def next_player(self) -> Optional[Player]:
        """获取下一个玩家"""
        if not self.players:
            return None
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return self.get_current_player()

    def start_round(self) -> bool:
        """开始新一轮"""
        if len(self.players) != self.max_players:
            return False
        
        if not self.wall:
            self.wall = Wall()
        
        self.round += 1
        self.current_player_index = self.dealer_index
        return True

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
            old_wind = old_assignments[player.name]
            new_wind_index = (winds.index(old_wind) + 1) % len(winds)
            self.wind_assignments[player.name] = winds[new_wind_index]
            player.seat_wind = winds[new_wind_index]

    def initialize_wall(self) -> None:
        """初始化牌墙"""
        self.wall = Wall()
        if self.wall:
            self.wall.shuffle()
        
    def deal_initial_tiles(self) -> bool:
        """发初始手牌"""
        if len(self.players) != self.max_players or not self.wall:
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

    def next_dealer(self):
        """移交庄家"""
        self.dealer_index = (self.dealer_index + 1) % len(self.players)

    def next_round(self) -> None:
        """进入下一轮"""
        self.round += 1
        if self.round > 4:
            self.round = 1
            self.round_wind = (self.round_wind + 1) % 4
