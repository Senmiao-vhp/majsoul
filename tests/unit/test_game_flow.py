import pytest
from src.core import tile
from src.core.game import Game
from src.core.game.flow import GameFlow
from src.core.game.score import ScoreCalculator
from src.core.game.state import ActionPriority
from src.core.game.state import GameState
from src.core.player import Player
from src.core.player.state import PlayerState
from src.core.tile import Tile, TileSuit
from src.core.yaku.judger import YakuJudger

def test_action_priority():
    """测试操作优先级"""
    game = Game()
    flow = GameFlow(game)
    
    # 创建测试玩家
    players = [Player(f"Player_{i}") for i in range(4)]
    for player in players:
        game.table.add_player(player)
    
    # 设置不同玩家的等待状态
    players[0].set_state(PlayerState.WAITING_CHI)
    players[1].set_state(PlayerState.WAITING_PON)
    players[2].set_state(PlayerState.WAITING_KAN)
    
    # 测试优先级判断
    assert flow._get_current_priority() == ActionPriority.KAN
    
    # 测试低优先级操作
    assert not flow.handle_player_action(players[0], ActionPriority.CHI)
    
    # 测试高优先级操作
    assert flow.handle_player_action(players[2], ActionPriority.KAN)

def test_win_check():
    """测试和牌判定"""
    game = Game()
    flow = GameFlow(game)
    player = Player("Test")
    game.table.add_player(player)
    
    # 设置游戏状态
    game.set_state(GameState.PLAYING)
    
    # 测试振听状态
    player.is_furiten = True
    assert not flow.check_win(player)
    
    # 测试非振听状态
    player.is_furiten = False
    # TODO: 添加更多和牌判定测试用例 

def test_action_priority_with_ron():
    """测试和牌优先级"""
    game = Game()
    flow = GameFlow(game)
    
    # 创建测试玩家
    players = [Player(f"Player_{i}") for i in range(4)]
    for player in players:
        game.table.add_player(player)
    
    # 设置不同玩家的等待状态
    players[0].set_state(PlayerState.WAITING_CHI)
    players[1].set_state(PlayerState.WAITING_PON)
    players[2].set_state(PlayerState.WAITING_RON)
    
    # 测试优先级判断
    assert flow._get_current_priority() == ActionPriority.RON
    
    # 测试低优先级操作
    assert not flow.handle_player_action(players[0], ActionPriority.CHI)
    assert not flow.handle_player_action(players[1], ActionPriority.PON)
    
    # 测试高优先级操作
    assert flow.handle_player_action(players[2], ActionPriority.RON)
    
    # 验证其他玩家状态被清除
    assert players[0].state == PlayerState.WAITING
    assert players[1].state == PlayerState.WAITING

def test_clear_waiting_players():
    """测试清除等待玩家状态"""
    game = Game()
    flow = GameFlow(game)
    
    # 创建测试玩家
    players = [Player(f"Player_{i}") for i in range(4)]
    for player in players:
        game.table.add_player(player)
    
    # 设置等待状态
    for player in players:
        player.set_state(PlayerState.WAITING_CHI)
    
    # 测试清除状态(保留一个玩家)
    flow._clear_waiting_players(except_player=players[0])
    
    # 验证结果
    assert players[0].state == PlayerState.WAITING_CHI
    for player in players[1:]:
        assert player.state == PlayerState.WAITING

def test_dealing_phase():
    """测试发牌阶段"""
    game = Game()
    flow = GameFlow(game)
    
    # 添加玩家
    for i in range(4):
        game.table.add_player(Player(f"Player_{i}"))
    
    # 测试发牌
    flow.start_dealing()
    
    # 验证发牌结果
    for player in game.table.players:
        assert len(player.hand.tiles) == 13
    assert game.get_state() == GameState.PLAYING
    assert game.table.get_current_player().state == PlayerState.THINKING

def test_discard_phase():
    """测试出牌阶段"""
    game = Game()
    flow = GameFlow(game)
    
    # 添加玩家
    for i in range(4):
        game.table.add_player(Player(f"Player_{i}"))
    
    # 设置游戏状态
    game.set_state(GameState.PLAYING)
    current_player = game.table.get_current_player()
    current_player.set_state(PlayerState.THINKING)
    
    # 添加测试用牌
    tile = Tile(TileSuit.MAN, 1)
    current_player.hand.add_tile(tile)
    
    # 测试出牌
    assert flow.handle_discard(current_player, tile)
    assert current_player.state == PlayerState.DISCARDING
    assert len(current_player.discards) == 1
    assert current_player.discards[-1] == tile

def test_player_state_transitions():
    """测试玩家状态切换"""
    game = Game()
    flow = GameFlow(game)
    
    # 添加玩家
    for i in range(4):
        game.table.add_player(Player(f"Player_{i}"))
    
    player = game.table.get_current_player()
    
    # 测试思考->出牌状态切换
    player.set_state(PlayerState.THINKING)
    tile = Tile(TileSuit.MAN, 1)
    player.hand.add_tile(tile)
    flow.handle_discard(player, tile)
    assert player.state == PlayerState.DISCARDING
    
    # 测试出牌->等待状态切换
    flow.end_discard_phase(player)
    assert player.state == PlayerState.WAITING

def test_turn_end_handling():
    """测试回合结束处理"""
    game = Game()
    flow = GameFlow(game)
    
    # 添加玩家
    for i in range(4):
        game.table.add_player(Player(f"Player_{i}"))
    
    # 设置游戏状态
    game.set_state(GameState.PLAYING)
    current_player = game.table.get_current_player()
    
    # 测试回合结束
    flow.end_turn(current_player)
    next_player = game.table.get_current_player()
    assert next_player != current_player
    assert next_player.state == PlayerState.THINKING
    assert current_player.state == PlayerState.WAITING

def test_ron_check():
    """测试荣和检查"""
    game = Game()
    flow = GameFlow(game)
    
    # 添加玩家
    for i in range(4):
        game.table.add_player(Player(f"Player_{i}"))
    
    # 设置玩家手牌为听牌状态
    player = game.table.players[1]
    tiles = [
        Tile(TileSuit.SOU, 2), Tile(TileSuit.SOU, 3),
        Tile(TileSuit.SOU, 4), Tile(TileSuit.SOU, 5),
        Tile(TileSuit.SOU, 6), Tile(TileSuit.SOU, 7),
        Tile(TileSuit.SOU, 8), Tile(TileSuit.SOU, 9),
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 1), Tile(TileSuit.PIN, 1),
        Tile(TileSuit.PIN, 1)
    ]
    for tile in tiles:
        player.hand.add_tile(tile)
    
    # 测试荣和
    flow.check_other_players_win(game.table.players[0], Tile(TileSuit.SOU, 1))
    assert player.state == PlayerState.WAITING_RON

def test_player_action():
    """测试玩家行动"""
    game = Game()
    flow = GameFlow(game)
    
    # 添加玩家
    for i in range(4):
        game.table.add_player(Player(f"Player_{i}"))
    
    # 设置游戏状态
    game.set_state(GameState.PLAYING)
    player = game.table.get_current_player()
    
    if player is None:
        pytest.fail("Current player should not be None")
        
    # 设置玩家状态为思考中
    player.set_state(PlayerState.THINKING)
    
    tile = Tile(TileSuit.MAN, 1)
    player.hand.add_tile(tile)
    assert flow.handle_discard(player, tile) is True

def test_win_with_riichi():
    """测试立直和牌"""
    game = Game()
    flow = GameFlow(game)
    game.set_state(GameState.PLAYING)

    # 设置非第一巡
    flow.first_turn = False
    flow.first_draw = False
    
    # 添加玩家
    for i in range(4):
        game.table.add_player(Player(f"Player_{i}"))
    
    # 设置玩家立直状态和手牌
    player = game.table.players[0]
    player.is_riichi = True
    player.set_state(PlayerState.THINKING)
    
    # 设置一个和牌型
    tiles = [        
        Tile(TileSuit.SOU, 2), Tile(TileSuit.SOU, 3),
        Tile(TileSuit.SOU, 4), Tile(TileSuit.SOU, 5),
        Tile(TileSuit.SOU, 6), Tile(TileSuit.SOU, 7),
        Tile(TileSuit.SOU, 8), Tile(TileSuit.SOU, 9),
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 1), Tile(TileSuit.PIN, 1),
        Tile(TileSuit.PIN, 1)
    ]
    for tile in tiles:
        player.hand.add_tile(tile)
        
    # 添加自摸牌
    winning_tile = Tile(TileSuit.SOU, 1)
    player.hand.add_tile(winning_tile)
    
    # 记录初始里宝牌数量
    initial_uradora_count = len(game.table.wall.uradora_indicators)
    
    # 测试自摸和牌
    assert flow.handle_win(player, winning_tile)
    assert len(game.table.wall.uradora_indicators) == initial_uradora_count + 1
    assert game.get_state() == GameState.FINISHED

def test_win_handling():
    """测试和牌处理"""
    game = Game()
    flow = GameFlow(game)
    game.set_state(GameState.PLAYING)  # 设置游戏状态
    
    # 添加玩家
    for i in range(4):
        game.table.add_player(Player(f"Player_{i}"))
    
    # 设置玩家状态和手牌
    player = game.table.players[0]
    player.is_riichi = True
    player.set_state(PlayerState.THINKING)
    
    # 设置完整的七对子和牌型（14张）
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2),
        Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 3),
        Tile(TileSuit.MAN, 4), Tile(TileSuit.MAN, 4),
        Tile(TileSuit.MAN, 5), Tile(TileSuit.MAN, 5),
        Tile(TileSuit.MAN, 6), Tile(TileSuit.MAN, 6),
        Tile(TileSuit.MAN, 7), Tile(TileSuit.MAN, 7)
    ]
    for tile in tiles:
        player.hand.add_tile(tile)
    
    # 记录初始里宝牌数量
    initial_uradora_count = len(game.table.wall.uradora_indicators)
    
    # 测试自摸和牌
    win_tile = tiles[-1]  # 使用最后一张牌作为和牌
    assert flow.handle_win(player, win_tile, is_tsumo=True)
    assert len(game.table.wall.uradora_indicators) == initial_uradora_count + 1
    assert game.get_state() == GameState.FINISHED
    assert player.state == PlayerState.WIN

def test_win_score_calculation():
    """测试和牌点数计算"""
    game = Game()
    flow = GameFlow(game)
    game.set_state(GameState.PLAYING)

    judger = YakuJudger()
    # 添加玩家
    for i in range(4):
        player = Player(f"Player_{i}")
        player.points = 25000
        game.table.add_player(player)
    
    # 设置庄家
    dealer = game.table.players[0]
    game.table.dealer = dealer
    
    # 设置自摸玩家
    winner = game.table.players[1]
    winner.set_state(PlayerState.THINKING)
    
    # 设置和牌型
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2),
        Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 3),
        Tile(TileSuit.MAN, 4), Tile(TileSuit.MAN, 4),
        Tile(TileSuit.MAN, 5), Tile(TileSuit.MAN, 5),
        Tile(TileSuit.MAN, 6), Tile(TileSuit.MAN, 6),
        Tile(TileSuit.MAN, 7), Tile(TileSuit.MAN, 7)
    ]
    for tile in tiles:
        winner.hand.add_tile(tile)
    
    # 添加自摸牌
    win_tile = Tile(TileSuit.MAN, 7)
    result = judger.judge(tiles=tiles, win_tile=win_tile)
    
    # 记录初始点数
    initial_points = {p.name: p.points for p in game.table.players}
    
    # 测试自摸和牌
    assert flow.handle_win(winner, win_tile, is_tsumo=True)
    
    # 验证点数变化
    assert winner.points > initial_points[winner.name]  # 赢家点数增加
    assert dealer.points < initial_points[dealer.name]  # 庄家点数减少
    assert game.table.players[2].points < initial_points["Player_2"]  # 闲家点数减少
    assert game.table.players[3].points < initial_points["Player_3"]  # 闲家点数减少
    
    # 验证游戏状态
    assert game.get_state() == GameState.FINISHED
    assert winner.state == PlayerState.WIN

def test_furiten():
    """测试振听判定"""
    game = Game()
    flow = GameFlow(game)
    player = Player("Test")
    game.table.add_player(player)
    
    # 设置听牌状态
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 3),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), 
        Tile(TileSuit.PIN, 4), Tile(TileSuit.SOU, 2),
        Tile(TileSuit.SOU, 3), Tile(TileSuit.SOU, 4),
        Tile(TileSuit.HONOR, 1), Tile(TileSuit.HONOR, 1)
    ]
    for tile in tiles:
        player.hand.add_tile(tile)
    
    # 打出一张听牌
    discard = Tile(TileSuit.MAN, 4)
    player.add_discard(discard)
    
    # 测试振听判定
    assert flow._is_furiten(player, discard)

def test_ippatsu_state():
    """测试一发状态"""
    game = Game()
    flow = GameFlow(game)
    game.set_state(GameState.PLAYING)
    
    # 添加玩家
    for i in range(4):
        game.table.add_player(Player(f"Player_{i}"))
    
    player = game.table.players[0]
    player.set_state(PlayerState.THINKING)
    
    # 设置基本和牌型
    tiles = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 1),
        Tile(TileSuit.PIN, 2), Tile(TileSuit.PIN, 3), Tile(TileSuit.PIN, 4),
        Tile(TileSuit.SOU, 2), Tile(TileSuit.SOU, 3), Tile(TileSuit.SOU, 4),
        Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2),
        Tile(TileSuit.MAN, 3), Tile(TileSuit.MAN, 4)
    ]
    for tile in tiles:
        player.hand.add_tile(tile)
    
    # 测试立直后获得一发状态
    assert flow.handle_riichi(player)
    assert player in flow.ippatsu_players
    
    # 测试副露后失去一发状态
    other_player = game.table.players[1]
    other_player.set_state(PlayerState.THINKING)
    # 模拟打出一张2万
    discard_tile = Tile(TileSuit.MAN, 2)
    other_player.add_discard(discard_tile)

    # 第三位玩家进行副露
    player3 = game.table.players[2]
    # 设置玩家手牌中有两张2万用于碰
    player3.hand.add_tile(Tile(TileSuit.MAN, 2))
    player3.hand.add_tile(Tile(TileSuit.MAN, 2))
    player3.set_state(PlayerState.WAITING_PON)
    assert flow.handle_pon(player3, [discard_tile, Tile(TileSuit.MAN, 2), Tile(TileSuit.MAN, 2)])
    assert player not in flow.ippatsu_players
    
    # 测试过一巡后失去一发状态
    player4 = game.table.players[3]
    player4.set_state(PlayerState.THINKING)
    assert flow.handle_riichi(player4)
    assert player4 in flow.ippatsu_players
    
    # 模拟一巡
    for p in game.table.players:
        p.set_state(PlayerState.THINKING)
        tile = Tile(TileSuit.MAN, 1)
        p.hand.add_tile(tile)
        assert flow.handle_discard(p, tile)
        flow.end_discard_phase(p)
        
    assert player4 not in flow.ippatsu_players

def test_special_win_states():
    """测试特殊和牌状态"""
    game = Game()
    flow = GameFlow(game)
    game.set_state(GameState.PLAYING)
    
    # 添加玩家
    for i in range(4):
        player = Player(f"Player_{i}")
        game.table.add_player(player)
    
    # 设置庄家
    dealer = game.table.players[0]
    game.table.dealer = dealer
    
    # 测试天和
    assert flow.check_special_win(dealer) == "天和"
    assert flow.is_tenhou is True
    
    # 测试地和
    flow.is_tenhou = False  # 重置状态
    non_dealer = game.table.players[1]
    assert flow.check_special_win(non_dealer) == "地和"
    assert flow.is_chiihou is True
    
    # 测试人和
    flow.is_chiihou = False  # 重置状态
    flow.first_draw = False  # 模拟已经过了第一次摸牌
    assert flow.check_special_win(dealer) == "人和"
    assert flow.is_renhou is True
    
    # 测试普通和牌
    flow.is_renhou = False  # 重置状态
    flow.first_turn = False  # 模拟已经过了第一巡
    assert flow.check_special_win(dealer) is None
    assert not any([flow.is_tenhou, flow.is_chiihou, flow.is_renhou])