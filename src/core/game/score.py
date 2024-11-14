from typing import Dict, List, Optional
from src.core.player import Player
from src.core.game.state import GameState

class ScoreCalculator:
    """点数计算器"""
    
    def __init__(self):
        self.riichi_sticks = 0  # 立直棒数量
        self.honba_sticks = 0   # 本场数
        self.is_dealer_win = False  # 是否庄家和牌
        
    def calculate_win_score(self, base_score: int, is_dealer: bool, 
                          is_tsumo: bool) -> Dict[str, int]:
        """计算和牌点数
        Args:
            base_score: 基础点数
            is_dealer: 是否庄家
            is_tsumo: 是否自摸
        Returns:
            Dict: 包含各家应付点数
        """
        # 计算本场和立直棒点数
        extra = (self.honba_sticks * 300) + (self.riichi_sticks * 1000)
        
        if is_tsumo:
            if is_dealer:
                # 庄家自摸,闲家各付基础点数的2倍
                point = base_score * 2
                return {
                    'child': point + extra // 3,
                    'dealer': 0
                }
            else:
                # 闲家自摸,庄家付基础点数的2倍,闲家付基础点数
                return {
                    'child': base_score + extra // 3,
                    'dealer': base_score * 2 + extra // 3
                }
        else:
            # 荣和直接付基础点数
            return {
                'total': base_score + extra
            }
            
    def calculate_final_scores(self, players: List[Player], is_dealer_win: bool = False) -> Dict[str, int]:
        """计算终局顺位点
        Args:
            players: 所有玩家列表
            is_dealer_win: 是否庄家和牌
        Returns:
            Dict: 各家最终点数
        """
        # 按点数排序
        sorted_players = sorted(players, key=lambda p: p.points, reverse=True)
        
        # 计算顺位点
        results = {}
        for i, player in enumerate(sorted_players):
            if i == 0:  # 一位
                results[player.name] = player.points + 30000
            elif i == 1:  # 二位
                results[player.name] = player.points + 10000
            elif i == 2:  # 三位
                results[player.name] = player.points - 10000
            else:  # 四位
                results[player.name] = player.points - 30000
                
            # 如果是庄家和牌,连庄
            if is_dealer_win and player == players[0]:
                self.honba_sticks += 1
                
        return results
        
    def handle_dealer_win(self):
        """处理庄家和牌"""
        self.is_dealer_win = True
        self.honba_sticks += 1
        
    def handle_dealer_lose(self):
        """处理庄家输牌"""
        self.is_dealer_win = False
        self.honba_sticks = 0
        
    def handle_exhaustive_draw(self, dealer_tenpai: bool):
        """处理流局
        Args:
            dealer_tenpai: 庄家是否听牌
        """
        if dealer_tenpai:
            self.honba_sticks += 1
        else:
            self.honba_sticks = 0
        
    def add_riichi_stick(self):
        """添加立直棒"""
        self.riichi_sticks += 1
        
    def collect_riichi_sticks(self) -> int:
        """收集立直棒
        Returns:
            int: 立直棒数量
        """
        sticks = self.riichi_sticks
        self.riichi_sticks = 0
        return sticks
        
    def handle_exhaustive_draw_riichi(self, tenpai_players: List[Player]):
        """处理流局时的立直棒
        Args:
            tenpai_players: 听牌的玩家列表
        """
        # 如果有人立直,立直棒保留到下一局
        if any(p.is_riichi for p in tenpai_players):
            return
            
        # 否则立直棒平分给听牌的玩家
        if tenpai_players:
            sticks_per_player = (self.riichi_sticks * 1000) // len(tenpai_players)
            for player in tenpai_players:
                player.points += sticks_per_player
            self.riichi_sticks = 0
            
    def handle_special_draw(self, draw_type: str, players: List[Player]):
        """处理特殊流局
        Args:
            draw_type: 流局类型 ('four_riichi'|'four_kans'|'nine_terminals')
            players: 所有玩家列表
        """
        # 四家立直流局
        if draw_type == 'four_riichi':
            # 立直棒保留到下一局
            self.honba_sticks += 1
            return
            
        # 四杠散了
        elif draw_type == 'four_kans':
            # 本场数+1,立直棒保留
            self.honba_sticks += 1
            return
            
        # 九种九牌
        elif draw_type == 'nine_terminals':
            # 本场数+1,立直棒保留
            self.honba_sticks += 1
            return