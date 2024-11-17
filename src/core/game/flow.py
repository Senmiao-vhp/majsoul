from typing import Optional, List, Set, Dict
from src.core.game.state import ActionPriority
from src.core.player import Player
from src.core.player.state import PlayerState
from src.core.game.state import GameState
from src.core.tile import Tile, TileSuit
from src.core.game.score import ScoreCalculator
from src.core.yaku.judger import YakuJudger
from src.core.common.wind import Wind
import os
import json

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
        self.ippatsu_players: Set[Player] = set()  # 新增：跟踪一发状态的玩家
        self.first_turn = True  # 标记是否第一巡
        self.first_draw = True  # 标记是否第一次摸牌
        # 特殊和牌状态
        self.is_tenhou = False  # 天和
        self.is_chiihou = False  # 地和
        self.is_renhou = False  # 人和
        
        # 加载配置文件
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                  'assets', 'config', 'game.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"配置文件不存在: {config_path}")
            self.config = {}
            
        # 添加事件监听
        self.game.controller.events.on("win", self.handle_win)
        self.game.controller.events.on("exhaustive_draw", self.handle_exhaustive_draw)
        self.game.controller.events.on("special_draw", self.handle_special_draw)
    
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
        if not self.controller.handle_chi(player, tiles):
            return False
            
        # 清除所有玩家的一发状态
        self.clear_ippatsu()
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
        
        # 清除所有玩家的一发状态
        self.clear_ippatsu()
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
        
        # 扣除立直点数
        player.points -= 1000
        player.is_riichi = True
        self.score_calculator.add_riichi_stick()
        
        # 新增：设置一发状态
        self.ippatsu_players.add(player)
        
        # 立即检查四家立直
        if self.game.controller.check_special_draw() == 'four_riichi':
            self.game.controller.handle_exhaustive_draw()
            # 发送特殊流局事件
            self.game.events.emit("special_draw", "four_riichi")
        
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
        if player.state not in [PlayerState.THINKING, PlayerState.WAITING, PlayerState.WAITING_RON]:  # 修改这里，允许WAITING状态
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
            bool: 是否荣和
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
        Returns:
            bool: 是否振听
        """
        # 获取听牌列表
        waiting_tiles = player.hand.check_tenpai()
        
        # 没有听牌则不是振听
        if not waiting_tiles:
            return False
            
        # 检查全局振听
        if player.furiten.is_furiten:
            return True
            
        # 检查立直振听 - 立直后放弃和牌机会就不能再荣和
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
        """开始发牌"""
        # 发牌
        for player in self.game.table.players:
            for _ in range(13):
                tile = self.game.table.wall.draw()
                if tile:
                    player.hand.add_tile(tile)
    
        # 检查开局九种九牌
        for player in self.game.table.players:
            terminals = set()
            for tile in player.hand.tiles:
                if tile.is_terminal():
                    terminals.add(tile)
            if len(terminals) >= 9:
                # 发送九种九牌询问事件
                self.game.events.emit("nine_terminals_check", player)
                self.game.set_state(GameState.WAITING)
                return
    
        # 设置游戏状态
        self.game.set_state(GameState.PLAYING)
        self.game.table.get_current_player().set_state(PlayerState.THINKING)
    
    def _validate_discard(self, player: Player, tile: Tile) -> bool:
        """验证出牌是否合法
        Args:
            player: 出牌的玩家
            tile: 要打出的牌
        Returns:
            bool: 是否合法
        """
        if player is None:
            return False
        
        if not isinstance(player, Player):
            return False
        
        if not isinstance(tile, Tile):
            return False
        
        if player.state != PlayerState.THINKING:
            return False
        
        if tile not in player.hand.tiles:
            return False
        
        return True
    
    def handle_discard(self, player: Player, tile: Tile) -> bool:
        """处理出牌"""
        if not self._validate_discard(player, tile):
            return False
        
        # 移除手牌并添加到弃牌
        player.hand.discard_tile(tile)
        player.discards.append(tile)
        player.set_state(PlayerState.DISCARDING)
        
        # 如果是立直玩家的第二次切牌，清除其一发状态
        if player in self.ippatsu_players:
            self.clear_ippatsu(player)
        
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
        
        # 更新第一巡和第一次摸牌状态
        self.first_draw = False
        if all(len(p.discards) > 0 for p in self.game.table.players):
            self.first_turn = False
        
        # 切换到下一个玩家
        next_player = self.next_turn()
        if next_player:
            next_player.set_state(PlayerState.THINKING)
    
    def check_other_players_win(self, discard_player: Player, tile: Tile) -> None:
        """检查其他玩家是否可以荣和"""
        # 设置游戏状态为PLAYING
        self.game.set_state(GameState.PLAYING)
        
        for player in self.game.table.players:
            if player != discard_player:
                # 先检查手牌是否能和
                if player.hand.check_win(tile):  # 直接使用hand.check_win
                    player.set_state(PlayerState.WAITING_RON)
                    # 发送事件通知
                    self.game.events.emit("ron_available", player, tile)
    
    def handle_tsumo(self, player: Player) -> bool:
        """处理自摸"""
        if player.state != PlayerState.THINKING:
            return False
        
        # 检查是否可以自摸
        if not self._check_tsumo(player):
            return False
        
        # 处理和牌
        win_tile = player.hand.tiles[-1]  # 自摸牌
        if not self._handle_win(player, win_tile, is_tsumo=True):
            return False
        
        # 设置和牌状态
        player.set_state(PlayerState.WIN)
        self.game.set_state(GameState.FINISHED)
        return True
    
    def handle_ron(self, player: Player, tile: Tile) -> bool:
        """处理荣和"""
        if player.state != PlayerState.WAITING_RON:
            # 如果玩家处于立直状态且错过和牌,标记为立直振听
            if player.is_riichi and player.hand.check_win(tile):
                player.furiten.is_riichi_furiten = True
            return False
        
        # 检查是否可以荣和
        if not self._check_ron(player, tile):
            return False
        
        # 处理和牌
        if not self._handle_win(player, tile, is_tsumo=False):
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
    
    def _validate_win(self, player: Player) -> bool:
        """验证和牌是否合法
        Args:
            player: 要验证的玩家
        Returns:
            bool: 是否合法
        """
        if not player:
            return False
        
        if self.game.get_state() != GameState.PLAYING:
            return False
        
        if player.state not in [PlayerState.THINKING, PlayerState.WAITING_RON]:
            return False
        
        # 检查振听
        if player.is_furiten:
            return False
        
        return True
    
    def handle_win(self, player: Player, win_tile: Tile, is_tsumo: bool = False,
              is_rinshan: bool = False, is_chankan: bool = False) -> bool:
        """处理和牌
        Args:
            player: 和牌玩家
            win_tile: 和牌牌型
            is_tsumo: 是否自摸
            is_rinshan: 是否岭上开花
            is_chankan: 是否抢杠
        """
        if not self._validate_win(player):
            return False
        
        # 检查特殊和牌
        special_win = self.check_special_win(player)
        
        # 检查海底摸月和河底捞鱼
        is_haitei = self.check_haitei()
        is_houtei = self.check_houtei(player)
        
        # 必须传入和牌
        if win_tile is None:
            return False
        
        # 计算和牌结果
        result = self.yaku_judger.judge(
            tiles=player.hand.tiles,
            melds=player.hand.melds,
            win_tile=win_tile,
            is_tsumo=is_tsumo,
            is_riichi=player.is_riichi,
            is_ippatsu=player in self.ippatsu_players,
            is_rinshan=is_rinshan,
            is_chankan=is_chankan,
            is_haitei=is_haitei,
            is_houtei=is_houtei,
            is_tenhou=special_win == "天和",
            is_chiihou=special_win == "地和",
            is_renhou=special_win == "人和",
            player_wind=player.seat_wind.value if player.seat_wind else 27,  # 默认东风
            round_wind=self.game.table.round_wind + 27,
            dora_tiles=self.game.table.wall.dora_indicators,
            uradora_tiles=self.game.table.wall.uradora_indicators if player.is_riichi else [],
            kyoutaku_number=self.score_calculator.riichi_sticks,
            tsumi_number=self.score_calculator.honba_sticks
        )

        if result and result['score'] > 0:
            # 判断是否庄家
            is_dealer = player == self.game.table.dealer
            
            # 获取所有玩家
            players = self.game.table.players  # 获取当前游戏中的所有玩家

            # 计算点数
            scores = self.score_calculator.calculate_win_score(
                total=result['score'],
                is_dealer=is_dealer,
                is_tsumo=is_tsumo,
                players=players  # 传递 players 参数
            )
            
            # 执行点数移动
            for other_player in self.game.table.players:
                if other_player != player:
                    if other_player == self.game.table.dealer:
                        other_player.points -= scores['dealer']
                    else:
                        other_player.points -= scores['non_dealer']
            player.points += sum(scores.values())
            
            # 验证点数
            initial_points = sum(p.points for p in players) + self.score_calculator.honba_sticks * 300 + self.score_calculator.riichi_sticks * 1000
            self.score_calculator.validate_points(players, initial_points, result['score'])
            
            # 处理连庄
            if is_dealer:
                self.score_calculator.handle_dealer_win()
            else:
                self.score_calculator.handle_dealer_lose()
                self.game.table.next_dealer()  # 移交庄家
                
            # 如果是立直和牌，翻开里宝牌
            if player.is_riichi:
                self.game.table.wall.add_uradora_indicator()
                
            # 设置状态
            player.set_state(PlayerState.WIN)
            self.game.set_state(GameState.FINISHED)
            
            return True
        return False
    
    def check_ippatsu(self, player: Player) -> bool:
        """检查是否一发
        Args:
            player: 要检查的玩家
        Returns:
            bool: 是否一发
        """
        return player in self.ippatsu_players
        
    def clear_ippatsu(self, player: Optional[Player] = None) -> None:
        """清除一发状态
        Args:
            player: 指定玩家，如果为None则清除所有玩家
        """
        if player:
            self.ippatsu_players.discard(player)
        else:
            self.ippatsu_players.clear()
    
    def check_nine_terminals(self, player: Player) -> bool:
        """检查是否九种九牌
        Args:
            player: 要检查的玩家
        Returns:
            bool: 是否满足九种九牌条件
        """
        terminals = set()
        for tile in player.hand.tiles:
            if tile.is_terminal():
                terminals.add(tile)
        return len(terminals) >= 9
    
    def check_special_win(self, player: Player) -> Optional[str]:
        """检查特殊和牌状态"""
        if self.first_draw:
            if player == self.game.table.dealer:
                self.is_tenhou = True
                return "天和"
            else:
                self.is_chiihou = True
                return "地和"
        elif self.first_turn:
            self.is_renhou = True
            return "人和"
        return None
    
    def check_haitei(self) -> bool:
        """检查是否海底摸月
        Returns:
            bool: 是否海底摸月
        """
        # 检查牌山剩余数量
        remaining = self.game.table.wall.get_remaining_count()
        # 最后一张牌才是海底
        return remaining == 0
    
    def check_houtei(self, player: Player) -> bool:
        """检查是否河底捞鱼
        Args:
            player: 要检查的玩家
        Returns:
            bool: 是他河底捞鱼
        """
        # 检查牌山剩余数量
        remaining = self.game.table.wall.get_remaining_count()
        # 检查是否是他家打出的最后一张牌
        return remaining == 0 and player.state == PlayerState.WAITING_RON
    
    def check_special_draw(self) -> Optional[str]:
        """检查特殊流局"""
        # 从 GameController 移动过来的代码
        # 检查四家立直
        riichi_count = sum(1 for p in self.game.table.players if p.is_riichi)
        if riichi_count == 4:
            return 'four_riichi'
        
        # 检查四杠散了
        kan_count = sum(len([m for m in p.hand.melds if len(m) == 4]) 
                       for p in self.game.table.players)
        if kan_count == 4:
            return 'four_kans'
        
        # 检查九种九牌
        for player in self.game.table.players:
            terminals = set()
            for tile in player.hand.tiles:
                if tile.is_terminal():
                    terminals.add(tile)
            if len(terminals) >= 9:
                return 'nine_terminals'
        
        return None
    
    def handle_exhaustive_draw(self) -> bool:
        """处理流局"""
        # 检查特殊流局
        special_draw = self.check_special_draw()
        if special_draw:
            self.score_calculator.handle_special_draw(special_draw, self.game.table.players)
            self.game.controller.events.emit("special_draw", special_draw)
            self.game.set_state(GameState.FINISHED)
            return True
        
        # 普通流局处理
        tenpai_players = [p for p in self.game.table.players if p.is_tenpai()]
        dealer_tenpai = self.game.table.dealer in tenpai_players
        
        # 处理立直棒和连庄
        self.score_calculator.handle_exhaustive_draw_riichi(tenpai_players)
        self.score_calculator.handle_exhaustive_draw(dealer_tenpai)
        
        if not dealer_tenpai:
            self.game.table.next_dealer()
        
        self.game.set_state(GameState.FINISHED)
        self.game.controller.events.emit("exhaustive_draw", tenpai_players)
        return True
    
    def handle_special_draw(self, draw_type: str) -> None:
        """处理特殊流局
        Args:
            draw_type: 特殊流局类型
        """
        # 处理本场数
        if draw_type == 'four_riichi':
            # 四家立直时本场数+1
            self.score_calculator.honba_sticks += 1
        else:
            # 其他特殊流局重置本场数
            self.score_calculator.honba_sticks = 0
        
        # 处理立直棒
        tenpai_players = [p for p in self.game.table.players if p.is_tenpai()]
        self.score_calculator.handle_exhaustive_draw_riichi(tenpai_players)
    
    def _handle_win(self, player: Player, tile: Tile, is_tsumo: bool = False) -> bool:
        """处理和牌"""
        try:
            # 检查游戏状态
            if self.game.get_state() != GameState.PLAYING:
                return False
            
            # 检查玩家状态
            if player.state not in [PlayerState.THINKING, PlayerState.WAITING_RON]:
                return False
            
            # 检查振听
            if player.is_furiten:
                return False
            
            # 调用手牌类的和牌判定
            result = player.hand.check_win(tile)
            
            if result and result['score'] > 0:
                # 判断是否庄家
                is_dealer = player == self.game.table.dealer
                
                # 计算点数
                scores = self.score_calculator.calculate_win_score(
                    base_score=result['score'],
                    is_dealer=is_dealer,
                    is_tsumo=is_tsumo
                )
                
                # 执行点数移动
                for other_player in self.game.table.players:
                    if other_player != player:
                        if other_player == self.game.table.dealer:
                            other_player.points -= scores['dealer']
                        else:
                            other_player.points -= scores['non_dealer']
                player.points += sum(scores.values())
                
                # 验证点数
                initial_points = sum(p.points for p in self.game.table.players) + self.score_calculator.honba_sticks * 300 + self.score_calculator.riichi_sticks * 1000
                self.score_calculator.validate_points(self.game.table.players, initial_points, result['score'])
                
                # 处理连庄
                if is_dealer:
                    self.score_calculator.handle_dealer_win()
                else:
                    self.score_calculator.handle_dealer_lose()
                    self.game.table.next_dealer()  # 移交庄家
                    
                # 如果是立直和牌，翻开里宝牌
                if player.is_riichi:
                    self.game.table.wall.add_uradora_indicator()
                    
                # 设置状态
                player.set_state(PlayerState.WIN)
                self.game.set_state(GameState.FINISHED)
                
                return True
            return False

        except Exception as e:
            self.logger.error(f"处理和牌时出错: {str(e)}")
            return False