import pytest
from src.core.game import Game
from src.core.game.flow import GameFlow
from src.core.game.state import GameState
from src.core.player import Player
from src.core.wall import Wall
from src.core.tile import Tile, TileSuit

def test_wall_initialization():
    """测试牌墙初始化"""
    wall = Wall()
    assert wall.remaining_count == 122
    
    # 验证牌的分布
    suit_counts = {
        TileSuit.MAN: 0,
        TileSuit.PIN: 0,
        TileSuit.SOU: 0,
        TileSuit.HONOR: 0
    }
    
    # 计算所有牌的分布(包括王牌区)
    all_tiles = wall.tiles + wall.dead_wall_tiles
    for tile in all_tiles:
        suit_counts[tile.suit] += 1
    
    assert suit_counts[TileSuit.MAN] == 36
    assert suit_counts[TileSuit.PIN] == 36
    assert suit_counts[TileSuit.SOU] == 36
    assert suit_counts[TileSuit.HONOR] == 28

def test_wall_draw():
    """测试摸牌"""
    wall = Wall()
    initial_count = wall.remaining_count
    tile = wall.draw()
    
    assert tile is not None
    assert wall.remaining_count == initial_count - 1
    
    # 测试摸完所有牌
    while wall.remaining_count > 0:
        wall.draw()
    assert wall.draw() is None

def test_wall_shuffle():
    """测试洗牌"""
    wall1 = Wall()
    wall2 = Wall()
    
    # 记录初始牌序
    tiles1 = wall1.tiles.copy()
    tiles2 = wall2.tiles.copy()
    
    # 洗牌
    wall1.shuffle()
    wall2.shuffle()
    
    # 验证牌数没有变化
    assert len(wall1.tiles) == len(tiles1)
    assert len(wall2.tiles) == len(tiles2)
    
    # 验证牌序已经改变
    assert wall1.tiles != tiles1
    assert wall2.tiles != tiles2

def test_add_dora_indicator():
    """测试宝牌指示牌翻开"""
    wall = Wall()
    
    # 测试初始状态
    assert len(wall.dora_manager.dora_indicators) == 1
    
    # 测试翻开新宝牌
    for _ in range(4):  # 再翻4张，总共5张
        wall.add_dora_indicator()
    
    # 验证最终状态
    assert len(wall.dora_manager.dora_indicators) == 5
    
    # 测试超出限制
    wall.add_dora_indicator()  # 尝试再翻一张
    assert len(wall.dora_manager.dora_indicators) == 5  # 仍然是5张

def test_kan_dora():
    """测试杠宝牌"""
    wall = Wall()
    initial_dora_count = len(wall.dora_indicators)
    
    # 创建杠牌组
    tiles = [
        Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 1),
        Tile(TileSuit.MAN, 1)
    ]
    
    # 测试杠后翻新宝牌
    game = Game()
    flow = GameFlow(game)
    player = Player("Test")
    game.table.add_player(player)
    game.set_state(GameState.PLAYING)
    
    flow.handle_kan(player, tiles)
    assert len(game.table.wall.dora_indicators) == initial_dora_count + 1

def test_reveal_uradora():
    """测试里宝牌翻开"""
    wall = Wall()
    
    # 测试初始状态
    assert len(wall.uradora_indicators) == 1
    
    # 测试翻开新里宝牌
    for _ in range(4):  # 再翻4张，总共5张
        wall.reveal_uradora()
    
    # 验证最终状态
    assert len(wall.uradora_indicators) == 5
    
    # 测试超出限制
    wall.reveal_uradora()  # 尝试再翻一张
    assert len(wall.uradora_indicators) == 5  # 仍然是5张