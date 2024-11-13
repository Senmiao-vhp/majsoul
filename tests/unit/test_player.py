import pytest
from src.core.player import Player

def test_player_initialization():
    """测试Player类初始化"""
    player = Player("Test Player")
    assert player.name == "Test Player"
    assert player.hand == []
    assert player.points == 0

def test_player_points():
    """测试玩家分数操作"""
    player = Player("Test Player")
    # 测试设置分数
    player.set_points(25000)
    assert player.get_points() == 25000
    # 测试增加分数
    player.add_points(1000)
    assert player.get_points() == 26000 