from typing import Optional, List, Dict, Set
from src.core.player import Player
from src.core.tile import Tile, TileSuit
from src.core.game.state import GameState
from src.core.player.state import PlayerState
from src.core.events import EventEmitter
from enum import IntEnum
from src.core.hand import Hand
from src.core.game.score import ScoreCalculator
import logging
from src.core.game.state import ActionPriority

class GameController:
    def __init__(self, table):
        self.table = table
        self.state = GameState.WAITING
        self.events = EventEmitter()
        self.waiting_players: Dict[Player, Set[ActionPriority]] = {}
        self.logger = logging.getLogger(__name__)
        self.score_calculator = ScoreCalculator()
        
    def start_game(self) -> bool:
        """开始游戏"""
        if len(self.table.players) != 4:
            return False
            
        self.state = GameState.DEALING
        self.table.start_round()
        return True
        
    def process_turn(self, player: Player) -> None:
        """处理玩家回合"""
        if self.state != GameState.PLAYING:
            return
            
        # 摸牌
        tile = self.table.wall.draw()
        if tile:
            player.hand.add_tile(tile)
            player.set_state(PlayerState.THINKING)
        else:
            # 牌山摸完,进入流局
            self.state = GameState.FINISHED
            
    def handle_discard(self, player: Player, tile_index: int) -> bool:
        """处理打牌"""
        if not player or player.state != PlayerState.THINKING:
            return False
            
        # 打出选中的牌
        discarded = player.hand.discard_tile(tile_index)
        if not discarded:
            return False
            
        player.discards.append(discarded)
        self.events.emit("tile_discarded", player, discarded)
        
        # 检查其他玩家是否可以响应
        self._check_other_players_response(player, discarded)
        
        player.set_state(PlayerState.WAITING)
        return True
        
    def _check_other_players_response(self, discard_player: Player, tile: Tile) -> None:
        """检查其他玩家对打出牌的响应"""
        self.waiting_players.clear()
        
        for player in self.table.players:
            if player == discard_player:
                continue
                
            available_actions = set()
            
            # 检查是否可以碰
            if self._can_pon(player, tile):
                available_actions.add(ActionPriority.PON)
                player.set_state(PlayerState.WAITING_PON)
                self.waiting_players[player] = available_actions
                continue  # 如果可以碰，就不检查吃了
                
            # 检查是否可以吃(仅下家可以吃)
            if self._can_chi(player, tile) and self._is_next_player(discard_player, player):
                available_actions.add(ActionPriority.CHI)
                player.set_state(PlayerState.WAITING_CHI)
                self.waiting_players[player] = available_actions
                
    def _is_next_player(self, current: Player, target: Player) -> bool:
        """检查target是否是current的下家"""
        current_idx = self.table.players.index(current)
        target_idx = self.table.players.index(target)
        return (current_idx + 1) % 4 == target_idx
        
    def handle_player_action(self, player: Player, action: ActionPriority) -> bool:
        """处理玩家操作"""
        if player not in self.waiting_players:
            return False
            
        available_actions = self.waiting_players[player]
        if action not in available_actions:
            return False
            
        # 检查是否有更高优先级的玩家在等待
        for other_player, other_actions in self.waiting_players.items():
            if other_player == player:
                continue
            if max(other_actions, default=ActionPriority.NONE) > action:
                return False
                
        # 清除其他等待玩家
        self.waiting_players.clear()
        return True
        
    def _can_pon(self, player: Player, tile: Tile) -> bool:
        """检查是否可以碰"""
        count = 0
        for hand_tile in player.hand.tiles:
            if hand_tile == tile:
                count += 1
        return count >= 2
        
    def _can_chi(self, player: Player, tile: Tile) -> bool:
        """检查是否可以吃"""
        if tile.suit == TileSuit.HONOR:
            return False
            
        # 检查是否有连续的数字牌
        values = [t.value for t in player.hand.tiles if t.suit == tile.suit]
        if tile.value - 1 in values and tile.value - 2 in values:
            return True
        if tile.value - 1 in values and tile.value + 1 in values:
            return True
        if tile.value + 1 in values and tile.value + 2 in values:
            return True
            
        return False
        
    def handle_riichi(self, player: Player) -> bool:
        """处理立直声明"""
        if not player or self.state != GameState.PLAYING:
            return False
            
        if player.state != PlayerState.THINKING:
            return False
            
        # 检查点数是否足够
        if player.points < 1000:
            return False
            
        # 扣除立直点数
        player.points -= 1000
        player.is_riichi = True
        self.score_calculator.add_riichi_stick()
        
        # 立即检查四家立直
        if self.check_special_draw() == 'four_riichi':
            self.handle_exhaustive_draw()
            # 发送特殊流局事件
            self.events.emit("special_draw", "four_riichi")
        
        return True
        
    def handle_kan(self, player: Player, tiles: List[Tile]) -> bool:
        """处理杠操作"""
        if not player or self.state != GameState.PLAYING:
            return False
            
        if len(tiles) != 4:
            return False
            
        # 检查是否都是相同的牌
        first_tile = tiles[0]
        if not all(tile == first_tile for tile in tiles):
            return False
            
        # 添加杠到玩家副露
        player.hand.add_meld(tiles)
        self.events.emit("kan_declared", player, tiles)
        return True
        
    def check_exhaustive_draw(self) -> bool:
        """检查是否流局"""
        if self.state != GameState.PLAYING:
            return False
            
        # 检查牌山是否摸完
        if self.table.wall.get_remaining_count() > 0:
            return False
            
        self.state = GameState.FINISHED
        self.events.emit("exhaustive_draw")
        return True
        
    def next_turn(self) -> Optional[Player]:
        """切换到下一个玩家回合"""
        # 检查是否流局
        if self.check_exhaustive_draw():
            return None
            
        # 获取下一个玩家
        next_player = self.table.next_player()
        if next_player:
            self.process_turn(next_player)
            
        return next_player
        
    def handle_chi(self, player: Player, tiles: List[Tile]) -> bool:
        """处理吃牌
        
        Args:
            player: 要吃牌的玩家
            tiles: 吃牌组合(3张)
            
        Returns:
            bool: 吃牌是否成功
        """
        # 1. 检查游戏状态
        if self.state != GameState.PLAYING:
            self.logger.debug("Game not in PLAYING state")
            return False
        
        # 2. 检查玩家状态
        if player.state != PlayerState.WAITING_CHI:
            self.logger.debug(f"Player not in WAITING_CHI state, current state: {player.state}")
            return False
        
        # 3. 检查牌组是否合法
        if len(tiles) != 3:
            self.logger.debug(f"Invalid tiles count: {len(tiles)}")
            return False
        
        # 4. 检查是否是顺子
        sorted_tiles = sorted(tiles, key=lambda t: t.value)
        if not (sorted_tiles[0].suit == sorted_tiles[1].suit == sorted_tiles[2].suit):
            self.logger.debug("Tiles not in same suit")
            return False
        
        if not (sorted_tiles[0].value + 1 == sorted_tiles[1].value and 
                sorted_tiles[1].value + 1 == sorted_tiles[2].value):
            self.logger.debug("Tiles not in sequence")
            return False
        
        # 5. 检查玩家手牌中是否有对应的牌
        player_tiles = player.hand.tiles
        for tile in tiles[:-1]:  # 最后一张是其他玩家打出的牌
            if tile not in player_tiles:
                self.logger.debug(f"Player does not have tile: {tile}")
                return False
        # 6. 添加吃牌到玩家副露
        for tile in tiles[:-1]:
            player.hand.remove_tile(tile)
        player.hand.add_meld(tiles)
        
        # 7. 更新玩家状态
        player.set_state(PlayerState.THINKING)
        
        # 8. 发送事件
        self.events.emit("chi_declared", player, tiles)
        
        return True
        
    def handle_pon(self, player: Player, tiles: List[Tile]) -> bool:
        """处理碰牌"""
        if not self.handle_player_action(player, ActionPriority.PON):
            return False
            
        if len(tiles) != 3:
            return False
            
        # 检查是否都是相同的牌
        first_tile = tiles[0]
        if not all(tile == first_tile for tile in tiles):
            return False
            
        # 添加碰牌到玩家副露
        player.hand.add_meld(tiles)
        player.set_state(PlayerState.THINKING)
        self.events.emit("pon_declared", player, tiles)
        return True
        
    def handle_win(self, winner: Player, loser: Optional[Player] = None) -> bool:
        """处理和牌"""
        if self.state != GameState.PLAYING:
            return False
            
        # 只负责状态检查和事件发送
        self.events.emit("win", winner)
        return True
        
    def check_special_draw(self) -> Optional[str]:
        """检查特殊流局
        Returns:
            str: 流局类型,无特殊流局则返回None
        """
        # 检查四家立直
        riichi_count = sum(1 for p in self.table.players if p.is_riichi)
        if riichi_count == 4:
            return 'four_riichi'
            
        # 检查四杠散了
        kan_count = sum(len([m for m in p.hand.melds if len(m) == 4]) 
                       for p in self.table.players)
        if kan_count == 4:
            return 'four_kans'
            
        # 检查九种九牌
        for player in self.table.players:
            terminals = set()
            for tile in player.hand.tiles:
                if tile.is_terminal():
                    terminals.add(tile)
            if len(terminals) >= 9:
                return 'nine_terminals'
                
        return None
        
    def handle_exhaustive_draw(self) -> bool:
        """处理流局"""
        if self.state != GameState.PLAYING:
            return False
            
        # 检查特殊流局
        special_draw = self.check_special_draw()
        if special_draw:
            # 发送特殊流局事件
            self.events.emit("special_draw", special_draw)
            # 增加本场数
            self.score_calculator.add_honba_stick()
        else:
            # 发送普通流局事件
            self.events.emit("exhaustive_draw")
            # 增加本场数
            self.score_calculator.add_honba_stick()
        
        # 状态转换
        self.state = GameState.FINISHED
        return True