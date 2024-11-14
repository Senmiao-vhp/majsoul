from typing import Optional, List, Dict
from src.core.game.controller import ActionPriority
from src.core.player import Player
from src.core.player.state import PlayerState
from src.core.game.state import GameState
from src.core.tile import Tile, TileSuit
from src.core.game.score import ScoreCalculator
from src.core.yaku.judger import YakuJudger

class GameFlow:
    """游戏流程控制类"""
    
    def __init__(self, game):
        # 使用运行时导入避免循环引用
        from src.core.game import Game
        if not isinstance(game, Game):
            raise TypeError("game must be an instance of Game")
        self.game = game
        self.controller = game.controller
        self.score_calculator = ScoreCalculator()
        self.yaku_judger = YakuJudger()
        
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
        if tile.suit == TileSuit.HONOR:  # 字牌不能吃
            return False
        
        values = [t.value for t in player.hand.tiles if t.suit == tile.suit]
        target = tile.value
        
        # 检查是否可以构成顺子
        return (target-2 in values and target-1 in values) or \
               (target-1 in values and target+1 in values) or \
               (target+1 in values and target+2 in values)
    
    def handle_chi(self, player: Player, tiles: List[Tile]) -> bool:
        """处理吃牌
        
        Args:
            player: 要吃牌的玩家
            tiles: 吃牌组合(3张)
            
        Returns:
            bool: 吃牌是否成功
        """
        # 使用 controller 的实现
        return self.controller.handle_chi(player, tiles)
    
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
        
        # 翻开新的宝牌指示牌
        if len(self.game.table.wall.dora_indicators) < 5:  # 最多5个宝牌指示牌
            self.game.table.wall.add_dora_indicator()
        
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
        
        # 除立直点数
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
        """检查玩家是否和
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
        # 检查振听
        if self._is_furiten(player, tile):
            return False
            
        # 检查是否可以和牌
        if player.hand.check_win(tile):
            return True
        return False
    
    def _check_tsumo(self, player: Player) -> bool:
        """检查是否可以自摸"""
        return player.hand.check_win()
    
    def _is_furiten(self, player: Player, tile: Optional[Tile] = None) -> bool:
        """检查是否振听
        Args:
            player: 要检查的玩家
            tile: 当前打出的牌(可选)
        """
        # 获取听牌列表
        waiting_tiles = player.hand.check_tenpai()
        
        # 没有听牌则不是振听
        if not waiting_tiles:
            return False
            
        # 检查全局振听
        if player.furiten.is_furiten:
            return True
            
        # 检查立直振听
        if player.is_riichi and player.furiten.is_riichi_furiten:
            return True
            
        # 检查同巡振听
        if tile and tile in waiting_tiles:
            player.furiten.is_temporary_furiten = True
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
        if player is None:
            raise ValueError("Player cannot be None")
        
        if not isinstance(player, Player):
            raise TypeError("player must be an instance of Player")
        
        if not isinstance(tile, Tile):
            raise TypeError("tile must be an instance of Tile")
        
        if player.state != PlayerState.THINKING:
            return False
        
        if tile not in player.hand.tiles:
            return False
        
        # 移除手牌并添加到弃牌
        player.hand.discard_tile(tile)
        player.discards.append(tile)
        player.set_state(PlayerState.DISCARDING)
        
        # 检查其他玩家响应
        self.check_other_players_win(player, tile)
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
    
    def check_other_players_win(self, discard_player: Player, tile: Tile) -> None:
        """检查其他玩家是否可以荣和"""
        for player in self.game.table.players:
            if player != discard_player:
                # 检查是否可以和牌
                if player.hand.check_win(tile) and not self.check_furiten(player):
                    player.set_state(PlayerState.WAITING_RON)
                    # 可以添加事件通知
                    self.game.events.emit("ron_available", player, tile)
    
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
    
    def handle_game_end(self) -> Dict[str, int]:
        """处理终局结算"""
        if self.game.get_state() != GameState.FINISHED:
            return {}
        
        # 获取和牌玩家
        winner = next((p for p in self.game.table.players if p.state == PlayerState.WIN), None)
        
        # 计算最终得分
        is_dealer_win = winner == self.game.table.dealer if winner else False
        final_scores = self.score_calculator.calculate_final_scores(
            self.game.table.players,
            is_dealer_win
        )
        
        # 更新玩家点数
        for player in self.game.table.players:
            player.points = final_scores[player.name]
        
        # 发送终局事件
        self.game.events.emit("game_end", final_scores)
        
        return final_scores
    
    def handle_win(self, player: Player, tile: Optional[Tile] = None) -> bool:
        """处理和牌
        Args:
            player: 和牌的玩家
            tile: 和牌的牌，如果是自摸则为None
        Returns:
            bool: 是否和牌成功
        """
        if self.game.get_state() != GameState.PLAYING:
            return False
        
        # 检查是否可以和牌
        if tile:  # 荣和
            if not self._check_ron(player, tile):
                return False
            win_tile = tile
        else:  # 自摸
            if not self._check_tsumo(player):
                return False
            win_tile = player.hand.tiles[-1]  # 使用最后一张牌作为和牌
        
        # 如果是立直玩家，翻开里宝牌
        if player.is_riichi:
            self.game.table.wall.reveal_uradora()
        
        # 计算得分
        is_dealer = player == self.game.table.dealer
        result = self.yaku_judger.judge(
            tiles=player.hand.tiles,
            win_tile=win_tile,  # 使用确定的和牌
            is_tsumo=tile is None,
            is_riichi=player.is_riichi
        )
        
        scores = self.score_calculator.calculate_win_score(
            base_score=result['score'],
            is_dealer=is_dealer,
            is_tsumo=tile is None
        )
        
        # 处理连庄
        if is_dealer:
            self.score_calculator.handle_dealer_win()
        else:
            self.score_calculator.handle_dealer_lose()
            self.game.table.next_dealer()  # 移交庄家
        
        # 执行点数移动
        if tile:  # 荣和
            discarder = next(p for p in self.game.table.players if p.last_discard == tile)
            discarder.points -= scores['total']
            player.points += scores['total']
        else:  # 自摸
            for other in self.game.table.players:
                if other != player:
                    if other == self.game.table.dealer:
                        other.points -= scores['dealer']
                    else:
                        other.points -= scores['child']
            player.points += sum(scores.values())
        
        # 设置和牌状态
        player.set_state(PlayerState.WIN)
        self.game.set_state(GameState.FINISHED)
        return True