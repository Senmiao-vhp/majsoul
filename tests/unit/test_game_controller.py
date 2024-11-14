import pytest
from src.core.game.controller import GameController
from src.core.table import Table
from src.core.player import Player
from src.core.game.state import GameState
from src.core.player.state import PlayerState
from src.core.tile import Tile, TileSuit
def test_game_controller_init():
    """测试游戏控制器初始化"""
    table = Table()
    controller = GameController(table)
    assert controller.state == GameState.WAITING
    
def test_game_start():
    """测试游戏开始"""
    table = Table()
    controller = GameController(table)
    
    # 添加玩家
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
        
    assert controller.start_game() is True
    assert controller.state == GameState.DEALING
    
    # 手动切换到PLAYING状态
    controller.state = GameState.PLAYING
    
def test_turn_processing():
    """测试回合处理"""
    table = Table()
    controller = GameController(table)
    
    # 添加玩家并开始游戏
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
    controller.start_game()
    
    # 确保状态为PLAYING
    controller.state = GameState.PLAYING
    
    # 测试回合处理
    current_player = table.get_current_player()
    initial_tiles = len(current_player.hand.tiles)
    controller.process_turn(current_player)
    assert len(current_player.hand.tiles) == initial_tiles + 1

def test_handle_discard():
    """测试打牌处理"""
    table = Table()
    controller = GameController(table)
    
    # 添加玩家并开始游戏
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
    controller.start_game()
    controller.state = GameState.PLAYING
    
    # 获取当前玩家
    player = table.get_current_player()
    player.set_state(PlayerState.THINKING)
    
    # 添加测试用牌
    tile = Tile(TileSuit.MAN, 1)
    player.hand.add_tile(tile)
    
    # 测试打牌
    controller.handle_discard(player, 0)
    assert len(player.discards) == 1
    assert player.discards[0] == tile
    assert player.state == PlayerState.WAITING

def test_handle_riichi():
    """测试立直声明"""
    table = Table()
    controller = GameController(table)
    player = Player("Test")
    player.set_points(25000)
    table.add_player(player)
    
    # 设置游戏状态
    controller.state = GameState.PLAYING
    player.set_state(PlayerState.THINKING)
    
    # 测试立直
    assert controller.handle_riichi(player) is True
    assert player.is_riichi is True
    assert player.points == 24000  # 扣除1000点立直棒

def test_handle_kan():
    """测试杠操作"""
    table = Table()
    controller = GameController(table)
    player = Player("Test")
    table.add_player(player)
    
    # 设置游戏状态
    controller.state = GameState.PLAYING
    
    # 创建杠牌组
    tiles = [
        Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 1)
    ]
    
    # 测试杠
    assert controller.handle_kan(player, tiles) is True
    assert len(player.hand.melds) == 1
    assert len(player.hand.melds[0]) == 4

def test_exhaustive_draw():
    """测试流局"""
    table = Table()
    controller = GameController(table)
    
    # 添加玩家并开始游戏
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
    controller.start_game()
    controller.state = GameState.PLAYING
    
    # 模拟摸完所有牌
    while table.wall.get_remaining_count() > 0:
        table.wall.draw()
        
    # 检查流局
    assert controller.check_exhaustive_draw() is True
    assert controller.state == GameState.FINISHED

def test_next_turn():
    """测试回合切换"""
    table = Table()
    controller = GameController(table)
    
    # 添加玩家并开始游戏
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
    controller.start_game()
    
    # 设置游戏状态为PLAYING
    controller.state = GameState.PLAYING
    
    # 获取当前玩家
    current_player = table.get_current_player()
    
    # 测试切换到下一个玩家
    next_player = controller.next_turn()
    assert next_player is not None
    assert next_player != current_player
    assert next_player.state == PlayerState.THINKING

def test_next_turn_exhaustive_draw():
    """测试流局时的回合切换"""
    table = Table()
    controller = GameController(table)
    
    # 添加玩家并开始游戏
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
    controller.start_game()
    controller.state = GameState.PLAYING
    
    # 模拟摸完所有牌
    while table.wall.get_remaining_count() > 0:
        table.wall.draw()
    
    # 测试流局
    next_player = controller.next_turn()
    assert next_player is None
    assert controller.state == GameState.FINISHED

def test_player_response():
    """测试玩家响应"""
    table = Table()
    controller = GameController(table)
    
    # 添加玩家并开始游戏
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
    controller.start_game()
    controller.state = GameState.PLAYING
    
    # 设置玩家手牌以测试碰
    player = table.players[1]  # 第二个玩家
    tile = Tile(TileSuit.MAN, 1)
    player.hand.add_tile(tile)
    player.hand.add_tile(tile)
    
    # 测试其他玩家打出相同的牌
    controller._check_other_players_response(table.players[0], tile)
    assert player.state == PlayerState.WAITING_PON

def test_can_chi():
    """测试吃牌判断"""
    table = Table()
    controller = GameController(table)
    player = Player("Test")
    
    # 添加手牌
    player.hand.add_tile(Tile(TileSuit.MAN, 1))
    player.hand.add_tile(Tile(TileSuit.MAN, 2))
    
    # 测试可以吃的情况
    assert controller._can_chi(player, Tile(TileSuit.MAN, 3)) is True
    
    # 测试不能吃的情况（字牌）
    assert controller._can_chi(player, Tile(TileSuit.HONOR, 1)) is False
    
    # 测试不能吃的情况（不连续的数字）
    assert controller._can_chi(player, Tile(TileSuit.MAN, 5)) is False

def test_handle_chi():
    """测试吃牌处理"""
    table = Table()
    controller = GameController(table)
    player = Player("Test")
    table.add_player(player)
    
    # 设置游戏和玩家状态
    controller.state = GameState.PLAYING
    player.set_state(PlayerState.WAITING_CHI)
    
    # 创建吃牌组合
    tiles = [
        Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 2),
        Tile(TileSuit.MAN, 3)
    ]
    
    # 添加牌到玩家手牌
    player.hand.add_tile(tiles[0])
    player.hand.add_tile(tiles[1])
    
    # 测试吃牌
    result = controller.handle_chi(player, tiles)
    assert result is True, "吃牌处理失败"
    assert len(player.hand.melds) == 1, "副露数量不正确"
    assert player.state == PlayerState.THINKING, "玩家状态未正确更新"
    
    # 验证副露内容
    meld = player.hand.melds[0]
    assert len(meld) == 3, "副露牌数量不正确"
    assert all(t1 == t2 for t1, t2 in zip(sorted(meld), sorted(tiles))), "副露牌内容不正确"

def test_special_draw():
    """测试特殊流局"""
    table = Table()
    controller = GameController(table)
    
    # 添加玩家
    for i in range(4):
        player = Player(f"Player_{i}")
        table.add_player(player)
        player.is_riichi = True  # 设置所有玩家立直
    
    # 设置游戏状态
    controller.state = GameState.PLAYING
    
    # 测试四家立直流局
    assert controller.check_special_draw() == 'four_riichi'
    assert controller.handle_exhaustive_draw() is True
    assert controller.state == GameState.FINISHED
    assert controller.score_calculator.honba_sticks == 1