import pytest
import pygame
from src.ui.renderer import GameRenderer
from src.core.game import Game
from src.core.table import Table
from src.core.wall import Wall

def test_renderer_init():
    """测试渲染器初始化"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    renderer = GameRenderer(screen)
    assert renderer.width == 800
    assert renderer.height == 600
    pygame.quit()

def test_render_game():
    """测试游戏渲染"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    renderer = GameRenderer(screen)
    game = Game()
    game.initialize()
    
    # 测试渲染不会抛出异常
    try:
        renderer.render_game(game)
    except Exception as e:
        pytest.fail(f"渲染失败: {e}")
    
    pygame.quit()

def test_render_wall_count():
    """测试牌数显示渲染"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    renderer = GameRenderer(screen)
    game = Game()
    game.initialize()
    
    # 测试正常渲染
    try:
        renderer._render_wall_count(game)
    except Exception as e:
        pytest.fail(f"渲染失败: {e}")
    
    # 测试无牌墙情况
    game.table.wall = None
    renderer._render_wall_count(game)  # 不应抛出异常
    
    pygame.quit()

def test_render_hand():
    """测试手牌渲染"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    renderer = GameRenderer(screen)
    game = Game()
    game.initialize()
    
    # 测试正常渲染
    try:
        renderer._render_hands(game)
    except Exception as e:
        pytest.fail(f"手牌渲染失败: {e}")
    
    # 测试空手牌渲染
    game.players[0].hand.tiles.clear()
    renderer._render_hands(game)  # 不应抛出异常
    
    pygame.quit()

def test_render_current_player():
    """测试当前玩家标记渲染"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    renderer = GameRenderer(screen)
    game = Game()
    game.initialize()
    
    try:
        renderer._render_current_player(game)
    except Exception as e:
        pytest.fail(f"当前玩家标记渲染失败: {e}")
    
    pygame.quit() 