import pytest
from src.core.game import Game
from src.core.game.state import GameState
from src.core.player import Player
from src.core.player.state import PlayerState
from src.core.table import Table
from src.core.game.controller import GameController
from src.core.game.flow import GameFlow
from src.core.tile import Tile, TileSuit

def test_four_riichi():
    """测试四家立直流局"""
    # 初始化
    table = Table()
    controller = GameController(table)
    
    # 添加玩家
    for i in range(4):
        player = Player(f"Player_{i}")
        player.points = 25000
        table.add_player(player)
    
    # 设置游戏状态
    controller.state = GameState.PLAYING
    
    # 让所有玩家立直
    for player in table.players:
        player.state = PlayerState.THINKING
        assert controller.handle_riichi(player)
    
    # 验证结果
    assert controller.state == GameState.FINISHED
    assert controller.score_calculator.honba_sticks == 1

def test_nine_terminals_at_start():
    """测试开局九种九牌"""
    game = Game()
    flow = GameFlow(game)
    
    # 添加玩家
    for i in range(4):
        game.table.add_player(Player(f"Player_{i}"))
    
    # 设置玩家手牌为九种九牌
    player = game.table.players[0]
    terminals = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 9),
        Tile(TileSuit.PIN, 1), Tile(TileSuit.PIN, 9),
        Tile(TileSuit.SOU, 1), Tile(TileSuit.SOU, 9),
        Tile(TileSuit.HONOR, 1), Tile(TileSuit.HONOR, 2),
        Tile(TileSuit.HONOR, 3)
    ]
    for tile in terminals:
        player.hand.add_tile(tile)
    
    # 补充剩余手牌
    for _ in range(4):
        player.hand.add_tile(Tile(TileSuit.MAN, 5))
    
    # 记录事件
    events = []
    def on_nine_terminals_check(p):
        events.append(("nine_terminals_check", p))
    game.events.on("nine_terminals_check", on_nine_terminals_check)
    
    # 测试开局检查
    flow.start_dealing()
    
    # 验证结果
    assert game.get_state() == GameState.WAITING
    assert len(events) == 1
    assert events[0] == ("nine_terminals_check", player)

def test_nine_terminals_choice():
    """测试九种九牌选择"""
    game = Game()
    flow = GameFlow(game)
    
    # 添加玩家
    for i in range(4):
        game.table.add_player(Player(f"Player_{i}"))
    
    # 设置玩家手牌为九种九牌
    player = game.table.players[0]
    terminals = [
        Tile(TileSuit.MAN, 1), Tile(TileSuit.MAN, 9),
        Tile(TileSuit.PIN, 1), Tile(TileSuit.PIN, 9),
        Tile(TileSuit.SOU, 1), Tile(TileSuit.SOU, 9),
        Tile(TileSuit.HONOR, 1), Tile(TileSuit.HONOR, 2),
        Tile(TileSuit.HONOR, 3)
    ]
    for tile in terminals:
        player.hand.add_tile(tile)
    
    # 补充剩余手牌
    for _ in range(4):
        player.hand.add_tile(Tile(TileSuit.MAN, 5))
    
    # 验证九种九牌检测
    assert flow.check_nine_terminals(player)
    
    # 模拟发牌
    flow.start_dealing()
    
    # 验证游戏状态为等待
    assert game.get_state() == GameState.WAITING