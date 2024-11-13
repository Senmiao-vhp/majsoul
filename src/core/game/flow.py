from typing import Optional, List
from src.core.game.controller import ActionPriority
from src.core.player import Player
from src.core.player.state import PlayerState
from src.core.game.state import GameState
from src.core.tile import Tile, TileSuit

class GameFlow:
    """游戏流程控制类"""
    
    def __init__(self, game):
        # 使用运行时导入避免循环引用
        from src.core.game import Game
        if not isinstance(game, Game):
            raise TypeError("game must be an instance of Game")
        self.game = game
        
    def start_turn(self, player: Player) -> None:
        """开始玩家回合"""
        if not player or self.game.get_state() != GameState.PLAYING:
            return
            
        # 摸牌
        tile = self.game.table.wall.draw()
        if tile:
            player.hand.add_tile(tile)
            player.set_state(PlayerState.THINKING)
        else:
            # 牌山摸完,进入流局
            self.game.set_state(GameState.FINISHED)
    
    def end_turn(self, player: Player) -> None:
        """结束玩家回合"""
        if not player or self.game.get_state() != GameState.PLAYING:
            return
            
        # 玩家回合结束,进入下一个玩家回合
        self.game.next_turn()
    
    def get_current_player(self) -> Optional[Player]:
        """获取当前玩家"""
        return self.game.get_current_player() 
    
    def process_discard(self, player: Player, tile_index: int) -> None:
        """处理玩家打牌"""
        if not player or self.game.get_state() != GameState.PLAYING:
            return
        
        if player.state != PlayerState.THINKING:
            return
        
        # 检查索引有效性
        if tile_index < 0 or tile_index >= len(player.hand.tiles):
            return
        
        # 打出选中的牌
        discarded_tile = player.hand.discard_tile(tile_index)
        if not discarded_tile:
            return
        
        # 添加到玩家的打牌记录
        player.discards.append(discarded_tile)
        
        # 设置玩家状态为等待
        player.set_state(PlayerState.WAITING)
        
        # 检查其他玩家是否可以吃碰杠
        self.check_other_players_response(player, discarded_tile)
        
        # 如果没有玩家可以操作,进入下一个玩家回合
        if not self.has_waiting_players():
            self.end_turn(player)
    
    def check_other_players_response(self, discard_player: Player, tile: Tile) -> None:
        """检查其他玩家对打出牌的响应"""
        for player in self.game.table.players:
            if player == discard_player:
                continue
            
            # 检查是否可以杠
            if self.can_kan(player, tile):
                player.set_state(PlayerState.WAITING_KAN)
                continue
            
            # 检查是否可以碰
            if self.can_pon(player, tile):
                player.set_state(PlayerState.WAITING_PON)
                continue
            
            # 检查是否可以吃(仅下家可以吃)
            if self.can_chi(player, tile) and self.is_next_player(discard_player, player):
                player.set_state(PlayerState.WAITING_CHI)
    
    def has_waiting_players(self) -> bool:
        """检查是否有玩家在等待响应"""
        return any(player.state in [PlayerState.WAITING_CHI, PlayerState.WAITING_PON, PlayerState.WAITING_KAN] 
                  for player in self.game.table.players)
    
    def can_pon(self, player: Player, tile: Tile) -> bool:
        """检查玩家是否可以碰"""
        if player.is_riichi:  # 立直状态下不能碰
            return False
        count = sum(1 for t in player.hand.tiles if t == tile)
        return count >= 2
    
    def can_chi(self, player: Player, tile: Tile) -> bool:
        """检查玩家是否可以吃"""
        if player.is_riichi:  # 立直状态下不能吃
            return False
        if tile.suit in [TileSuit.HONOR, TileSuit.BONUS]:  # 字牌和花牌不能吃
            return False
        
        values = [t.value for t in player.hand.tiles if t.suit == tile.suit]
        target = tile.value
        
        # 检查是否可以构成顺子
        return (target-2 in values and target-1 in values) or \
               (target-1 in values and target+1 in values) or \
               (target+1 in values and target+2 in values)
    
    def handle_chi(self, player: Player, tiles: List[Tile]) -> bool:
        """处理吃牌"""
        if player.state != PlayerState.WAITING_CHI:
            return False
        
        if len(tiles) != 3:
            return False
        
        # 检查是否是同一花色
        suit = tiles[0].suit
        if not all(tile.suit == suit for tile in tiles):
            return False
        
        # 检查是否是连续的数字
        values = sorted([tile.value for tile in tiles])
        if values[1] != values[0] + 1 or values[2] != values[1] + 1:
            return False
        
        # 添加吃牌到玩家副露
        player.hand.add_meld(tiles)
        player.set_state(PlayerState.THINKING)
        return True
    
    def handle_pon(self, player: Player, tiles: List[Tile]) -> bool:
        """处理碰牌"""
        if player.state != PlayerState.WAITING_PON:
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
        return True
    
    def handle_kan(self, player: Player, tiles: List[Tile]) -> bool:
        """处理杠操作"""
        if self.game.get_state() != GameState.PLAYING:
            return False
        
        if len(tiles) != 4:
            return False
        
        # 检查是否都是相同的牌
        first_tile = tiles[0]
        if not all(tile == first_tile for tile in tiles):
            return False
        
        # 添加杠到玩副露
        player.hand.add_meld(tiles)
        player.set_state(PlayerState.THINKING)
        return True
    
    def is_next_player(self, current: Player, target: Player) -> bool:
        """检查target是否是current的下家"""
        current_idx = self.game.table.players.index(current)
        target_idx = self.game.table.players.index(target)
        return (current_idx + 1) % len(self.game.table.players) == target_idx
    
    def handle_riichi(self, player: Player) -> bool:
        """处理立直声明"""
        if not player or self.game.get_state() != GameState.PLAYING:
            return False
        
        if player.state != PlayerState.THINKING:
            return False
        
        # 检查点数是否足够
        if player.points < 1000:
            return False
        
        # 扣除立直点数
        player.points -= 1000
        player.is_riichi = True
        return True
    
    def check_exhaustive_draw(self) -> bool:
        """检查是否流局"""
        if self.game.get_state() != GameState.PLAYING:
            return False
        
        # 检查牌山是否摸完
        if self.game.table.wall.get_remaining_count() > 0:
            return False
        
        self.game.set_state(GameState.FINISHED)
        return True
    
    def next_turn(self) -> Optional[Player]:
        """切换到下一个玩家回合"""
        # 检查是否流局
        if self.check_exhaustive_draw():
            return None
        
        # 获取下一个玩家
        next_player = self.game.table.next_player()
        if next_player:
            self.start_turn(next_player)
        
        return next_player
    
    def handle_player_action(self, player: Player, action: ActionPriority) -> bool:
        """处理玩家操作"""
        if player.state not in [PlayerState.WAITING_CHI, PlayerState.WAITING_PON, 
                               PlayerState.WAITING_KAN, PlayerState.WAITING_RON]:
            return False
        
        # 检查操作优先级
        current_priority = self._get_current_priority()
        if action.value < current_priority.value:
            return False
        
        # 清除其他等待玩家状态
        self._clear_waiting_players(except_player=player)
        return True
    
    def _get_current_priority(self) -> ActionPriority:
        """获取当前最高优先级操作"""
        highest_priority = ActionPriority.NONE
        for player in self.game.table.players:
            if player.state == PlayerState.WAITING_RON:
                highest_priority = max(highest_priority, ActionPriority.RON)
            elif player.state == PlayerState.WAITING_KAN:
                highest_priority = max(highest_priority, ActionPriority.KAN)
            elif player.state == PlayerState.WAITING_PON:
                highest_priority = max(highest_priority, ActionPriority.PON)
            elif player.state == PlayerState.WAITING_CHI:
                highest_priority = max(highest_priority, ActionPriority.CHI)
        return highest_priority
    
    def can_kan(self, player: Player, tile: Tile) -> bool:
        """检查玩家是否可以杠"""
        if player.is_riichi:  # 立直状态下不能杠
            return False
        count = sum(1 for t in player.hand.tiles if t == tile)
        return count >= 3
    
    def check_win(self, player: Player, tile: Optional[Tile] = None) -> bool:
        """检查玩家是否和牌
        Args:
            player: 要检查的玩家
            tile: 要检查的牌(荣和时传入)
        Returns:
            bool: 是否和牌
        """
        # 检查游戏状态
        if self.game.get_state() != GameState.PLAYING:
            return False
        
        # 检查玩家状态
        if player.state not in [PlayerState.THINKING, PlayerState.WAITING_RON]:
            return False
        
        # 检查是否振听
        if player.is_riichi and self._is_furiten(player, tile):
            return False
        
        # 调用手牌类的和牌判定
        return player.hand.check_win(tile)
    
    def _check_ron(self, player: Player, tile: Tile) -> bool:
        """检查是否可以荣和
        Args:
            player: 要检查的玩家
            tile: 打出的牌
        Returns:
            bool: 是否可以荣和
        """
        # 检查是否可以和牌
        if player.hand.check_win(tile):
            return True
        return False
    
    def _check_tsumo(self, player: Player) -> bool:
        """检查是否可以自摸"""
        return player.hand.check_win()
    
    def _is_furiten(self, player: Player, tile: Tile) -> bool:
        """检查是否振听"""
        # 检查最近一巡的打牌记录
        for discard in player.discards[-4:]:
            if discard == tile:
                return True
        return False
    
    def _clear_waiting_players(self, except_player: Optional[Player] = None) -> None:
        """清除等待玩家状态"""
        for player in self.game.table.players:
            if player != except_player and player.state in [
                PlayerState.WAITING_CHI, 
                PlayerState.WAITING_PON,
                PlayerState.WAITING_KAN,
                PlayerState.WAITING_RON
            ]:
                player.set_state(PlayerState.WAITING)
    
    def start_dealing(self) -> None:
        """开始发牌阶段"""
        if self.game.get_state() != GameState.WAITING:
            return
        
        self.game.set_state(GameState.DEALING)
        for player in self.game.table.players:
            player.set_state(PlayerState.DEALING)
            # 发13张牌
            for _ in range(13):
                tile = self.game.table.wall.draw()
                if tile:
                    player.hand.add_tile(tile)
        
        # 发牌完成后进入游戏阶段
        self.game.set_state(GameState.PLAYING)
        self.game.table.get_current_player().set_state(PlayerState.THINKING)
    
    def handle_discard(self, player: Player, tile: Tile) -> bool:
        """处理出牌"""
        if player.state != PlayerState.THINKING:
            return False
        
        if tile not in player.hand.tiles:
            return False
        
        # 移除手牌并添加到弃牌
        player.hand.discard_tile(tile)
        player.discards.append(tile)
        player.set_state(PlayerState.DISCARDING)
        
        # 检查其他玩家响应
        self.check_other_players_response(player, tile)
        return True
    
    def end_discard_phase(self, player: Player) -> None:
        """结束出牌阶段"""
        if player.state != PlayerState.DISCARDING:
            return
        
        player.set_state(PlayerState.WAITING)
        
        # 如果没有等待响应的玩家,进入下一回合
        if not self.has_waiting_players():
            self.end_turn(player)
    
    def end_turn(self, player: Player) -> None:
        """结束当前回合"""
        if self.game.get_state() != GameState.PLAYING:
            return
        
        # 切换到下一个玩家
        next_player = self.next_turn()
        if next_player:
            next_player.set_state(PlayerState.THINKING)
    
    def check_furiten(self, player: Player) -> bool:
        """检查振听
        Args:
            player: 要检查的玩家
        Returns:
            bool: 是否振听
        """
        # 获取听牌列表
        tenpai_tiles = player.hand.check_tenpai()
        if not tenpai_tiles:
            return False
        
        # 检查最近一巡的打牌记录
        for discard in player.discards[-4:]:
            if discard in tenpai_tiles:
                return True
        
        return False
    
    def check_other_players_win(self, discard_player: Player, tile: Tile) -> bool:
        """检查其他玩家是否可以荣和"""
        has_winner = False
        for player in self.game.table.players:
            if player != discard_player and self._check_ron(player, tile):
                player.set_state(PlayerState.WAITING_RON)
                has_winner = True
        return has_winner
    
    def handle_ron(self, player: Player, tile: Tile) -> bool:
        """处理荣和"""
        if player.state != PlayerState.WAITING_RON:
            return False
        
        # 检查是否可以荣和
        if not self._check_ron(player, tile):
            return False
        
        # 设置和牌状态
        player.set_state(PlayerState.WIN)
        self.game.set_state(GameState.FINISHED)
        return True
    
    def handle_tsumo(self, player: Player) -> bool:
        """处理自摸"""
        if player.state != PlayerState.THINKING:
            return False
        
        # 检查是否可以自摸
        if not self._check_tsumo(player):
            return False
        
        # 设置和牌状态
        player.set_state(PlayerState.WIN)
        self.game.set_state(GameState.FINISHED)
        return True