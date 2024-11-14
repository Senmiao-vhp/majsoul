import pytest
from src.core.game import Game
from src.core.game.flow import GameFlow
from src.core.game.controller import ActionPriority
from src.core.game.state import GameState
from src.core.player import Player
from src.core.player.state import PlayerState
from src.core.tile import Tile, TileSuit

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