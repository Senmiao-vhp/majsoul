import pytest
from src.core.table import Table, Wind
from src.core.player import Player

def test_table_seat_assignment():
    """测试座位分配"""
    table = Table()
    for i in range(4):
        player = Player(f"Player_{i}")
        table.add_player(player)
    
    table.assign_seats()
    assert table.players[0].seat_wind == Wind.EAST
    assert table.players[1].seat_wind == Wind.SOUTH 

def test_table_initialization():
    """测试牌桌初始化"""
    table = Table()
    assert len(table.players) == 0
    assert table.wall is not None
    assert table.round == 1
    assert table.dealer_index == 0
    assert table.current_player_index == 0
    
def test_wall_operations():
    """测试牌山操作"""
    table = Table()
    assert table.wall.get_remaining_count() == 136  # 初始136张牌
    
    # 测试发牌
    tile = table.wall.draw()
    assert tile is not None
    assert table.wall.get_remaining_count() == 135

def test_add_player():
    """测试添加玩家"""
    table = Table()
    player = Player("Test Player")
    assert table.add_player(player) is True
    assert len(table.players) == 1
    
    # 测试超出最大玩家数
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
    assert table.add_player(Player("Extra")) is False

def test_player_rotation():
    """测试玩家轮换"""
    table = Table()
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
        
    first_player = table.get_current_player()
    if first_player is None:
        pytest.fail("First player should not be None")
        
    next_player = table.next_player()
    if next_player is None:
        pytest.fail("Next player should not be None")
        
    assert first_player != next_player

def test_seat_assignment():
    """测试座位分配"""
    table = Table()
    players = [Player(f"Player_{i}") for i in range(4)]
    for player in players:
        table.add_player(player)
    
    table.assign_seats()
    assert table.get_player_wind(players[0]) == Wind.EAST
    assert table.get_player_wind(players[1]) == Wind.SOUTH
    assert table.get_player_wind(players[2]) == Wind.WEST
    assert table.get_player_wind(players[3]) == Wind.NORTH

def test_round_management():
    """测试牌局管理"""
    table = Table()
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
    
    # 测试开始新一轮
    assert table.start_round() is True
    assert table.round == 2
    assert table.current_player_index == table.dealer_index
    
    # 测试重置
    table.reset_round()
    assert table.round == 2
    assert table.current_player_index == 0
    assert table.dealer_index == 0
    assert len(table.wind_assignments) == 0

def test_incomplete_table():
    """测试人数不足的情况"""
    table = Table()
    # 只添加3个玩家
    for i in range(3):
        table.add_player(Player(f"Player_{i}"))
    
    assert table.start_round() is False
    assert table.get_current_player() is None

def test_table_round_management():
    """测试牌局管理"""
    table = Table()
    # 添加玩家
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
    
    # 测试开始新一轮
    assert table.start_round() is True
    assert table.round == 2
    assert table.current_player_index == table.dealer_index
    
    # 测试重置
    table.reset_round()
    assert table.round == 2
    assert table.current_player_index == 0
    assert table.dealer_index == 0
    assert len(table.wind_assignments) == 0

def test_round_operations():
    """测试牌局操作"""
    table = Table()
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
    
    # 测试开始新一轮
    initial_round = table.round
    assert table.start_round() is True
    assert table.round == initial_round + 1
    assert table.current_player_index == table.dealer_index
    
    # 测试重置当前轮
    table.reset_round()
    assert table.current_player_index == table.dealer_index
    for player in table.players:
        assert len(player.hand.tiles) == 0

def test_wind_rotation():
    """测试风位轮转"""
    table = Table()
    
    # 添加4个玩家
    for i in range(4):
        table.add_player(Player(f"Player_{i}"))
    
    # 初始分配座位
    table.assign_seats()
    initial_winds = {player.name: table.get_player_wind(player) 
                    for player in table.players}
    
    # 进行一次风位轮转
    table.rotate_winds()
    
    # 验证风位变化
    for player in table.players:
        old_wind = initial_winds[player.name]
        new_wind = table.get_player_wind(player)
        assert old_wind != new_wind