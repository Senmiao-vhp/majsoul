from typing import Dict, List
from src.core.player import Player

class ScoreCalculator:
    """点数计算器"""
    
    def __init__(self):
        self.riichi_sticks = 0  # 立直棒数量
        self.honba_sticks = 0   # 本场数
        self.is_dealer_win = False  # 是否庄家和牌
        
    def calculate_win_score(self, total: int, is_dealer: bool, is_tsumo: bool, players: List[Player]) -> Dict[str, int]:
        """计算和牌点数
        Args:
            total: 实际支付的总点数
            is_dealer: 是否庄家
            is_tsumo: 是否自摸
            players: 所有玩家列表
        Returns:
            Dict[str, int]: 点数字典，包含：
                - 'dealer': 庄家支付点数
                - 'non_dealer': 闲家支付点数
                - 'total': 总点数
        """
        initial_points = sum(player.points for player in players) + self.honba_sticks * 300 + self.riichi_sticks * 1000
        print(f"计算初始点数: {initial_points}")  # 调试输出
        
        if is_tsumo:
            if is_dealer:
                # 庄家自摸，所有人支付相同点数
                payment = total / 3  # 三家支付相同的点数
                # 收取立直棒并清零
                total += self.collect_riichi_sticks() * 1000  # 收取立直棒
                self.riichi_sticks = 0  # 清零立直棒
                return {
                    'dealer': 0,
                    'non_dealer': payment,
                    'total': total
                }
            else:
                # 闲家自摸，庄家支付2倍
                dealer_payment = total / 2
                non_dealer_payment = total / 4
                # 收取立直棒并清零
                total += self.collect_riichi_sticks() * 1000  # 收取立直棒
                self.riichi_sticks = 0  # 清零立直棒
                return {
                    'dealer': dealer_payment,
                    'non_dealer': non_dealer_payment,
                    'total': total
                }
        else:
            # 荣和，放铳者支付全部点数
            payment = total
            # 收取立直棒和场棒并清零
            total += self.collect_riichi_sticks() * 1000  # 收取立直棒
            total += self.honba_sticks * 300  # 收取场棒
            self.honba_sticks = 0  # 清零场棒
            
            # 计算点数
            current_points = sum(player.points for player in players) + self.honba_sticks * 300 + self.riichi_sticks * 1000
            print(f"计算当前点数: {current_points}")  # 调试输出

            # 返回点数
            return {
                'dealer': payment,
                'non_dealer': payment,
                'total': total  # 总点数
            }

    def validate_points(self, players: List[Player], initial_points: int, total: int):
        """验证点数是否正确
        Args:
            players: 所有玩家列表
            initial_points: 初始点数总和
            total: 当前点数总和
        """
        current_points = sum(player.points for player in players) + self.honba_sticks * 300 + self.riichi_sticks * 1000
        if current_points != initial_points:
            raise ValueError(f"点数验证失败: 初始点数总和 {initial_points} 与当前点数总和 {current_points} 不一致。计算点数{total}")

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
        
    def add_honba_stick(self):
        """添加本场棒"""
        self.honba_sticks += 1
        
    def collect_riichi_sticks(self) -> int:
        """收集立直棒
        Returns:
            int: 收集到的立直棒数量
        """
        sticks = self.riichi_sticks
        self.riichi_sticks = 0  # 清零立直棒
        return sticks
        
    def handle_exhaustive_draw_riichi(self, players: List[Player]):
        """处理流局时的立直棒分配
        Args:
            players: 参与分配的玩家列表
        """
        if not players:
            return
            
        # 平分立直棒
        sticks = self.collect_riichi_sticks()
        points_per_player = (sticks * 1000) // len(players)
        for player in players:
            player.points += points_per_player
        
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