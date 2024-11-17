from src.core.game.score import ScoreCalculator
from src.core.player import Player


def test_score_calculation():
    """测试点数计算"""
    calculator = ScoreCalculator()
    players = [Player("测试玩家")]  # 创建一个玩家列表
    
    # 测试荣和点数计算
    scores = calculator.calculate_win_score(2000, False, False, players)
    assert scores['total'] == 2000
    
    # 测试庄家自摸
    scores = calculator.calculate_win_score(12000, True, True, players)
    assert scores['non_dealer'] == 4000  # 修改为 'non_dealer'
    
    # 测试立直棒和本场数
    calculator.riichi_sticks = 2
    calculator.honba_sticks = 1
    scores = calculator.calculate_win_score(2000, False, False, players)
    assert scores['total'] == 2000 + 2000 + 300  # 2000 + 2000 + 300


def test_final_score_calculation():
    """测试终局结算"""
    calculator = ScoreCalculator()
    
    # 创建测试玩家
    players = []
    points = [30000, 25000, 24000, 21000]
    for i, point in enumerate(points):
        player = Player(f"Player_{i}")
        player.points = point
        players.append(player)
    
    # 测试普通终局
    results = calculator.calculate_final_scores(players)
    assert results["Player_0"] == 60000  # 30000 + 30000
    assert results["Player_1"] == 35000  # 25000 + 10000
    assert results["Player_2"] == 14000  # 24000 - 10000
    assert results["Player_3"] == -9000  # 21000 - 30000
    
    # 测试庄家和牌
    results = calculator.calculate_final_scores(players, True)
    assert calculator.honba_sticks == 1


def test_dealer_win():
    """测试庄家和牌"""
    calculator = ScoreCalculator()
    
    # 测试庄家和牌
    calculator.handle_dealer_win()
    assert calculator.is_dealer_win is True
    assert calculator.honba_sticks == 1
    
    # 测试连续和牌
    calculator.handle_dealer_win()
    assert calculator.honba_sticks == 2


def test_dealer_lose():
    """测试庄家输牌"""
    calculator = ScoreCalculator()
    calculator.honba_sticks = 2
    
    # 测试庄家输牌
    calculator.handle_dealer_lose()
    assert calculator.is_dealer_win is False
    assert calculator.honba_sticks == 0


def test_exhaustive_draw():
    """测试流局"""
    calculator = ScoreCalculator()
    calculator.honba_sticks = 1
    
    # 测试庄家听牌流局
    calculator.handle_exhaustive_draw(True)
    assert calculator.honba_sticks == 2
    
    # 测试庄家不听牌流局
    calculator.handle_exhaustive_draw(False)
    assert calculator.honba_sticks == 0


def test_riichi_stick_handling():
    """测试立直棒处理"""
    calculator = ScoreCalculator()
    
    # 测试添加立直棒
    calculator.add_riichi_stick()
    assert calculator.riichi_sticks == 1
    
    # 测试收集立直棒
    sticks = calculator.collect_riichi_sticks()
    assert sticks == 1
    assert calculator.riichi_sticks == 0
    
    # 测试流局时立直棒处理
    calculator.add_riichi_stick()
    calculator.add_riichi_stick()
    
    # 创建测试玩家
    players = []
    for i in range(2):
        player = Player(f"Player_{i}")
        player.points = 25000
        players.append(player)
    
    # 测试流局时立直棒平分
    calculator.handle_exhaustive_draw_riichi(players)
    assert calculator.riichi_sticks == 0
    assert all(p.points == 26000 for p in players)  # 每人分得1000点