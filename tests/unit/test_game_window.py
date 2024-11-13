import pytest
import pygame
from src.core.game.state import GameState
from src.ui import GameWindow

def test_game_window_init():
    """测试游戏窗口初始化"""
    window = GameWindow(800, 600)
    assert window.width == 800
    assert window.height == 600
    assert window.game is None
    assert isinstance(window.screen, pygame.Surface)
    pygame.quit()

def test_game_window_initialize():
    """测试游戏初始化"""
    window = GameWindow()
    window.initialize()
    assert window.game is not None
    pygame.quit()

def test_game_window_events():
    """测试事件处理"""
    window = GameWindow()
    
    # 测试退出事件
    event = pygame.event.Event(pygame.QUIT)
    pygame.event.post(event)
    assert window.handle_events() is False
    
    pygame.quit()

def test_mouse_click_handling():
    """测试鼠标点击处理"""
    pygame.init()
    window = GameWindow(800, 600)
    
    # 测试主菜单点击
    menu_click_pos = (window.width//2, window.height//2)  # 开始按钮位置
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": menu_click_pos})
    pygame.event.post(event)
    window.handle_events()
    assert window.game is not None
    
    # 测试游戏内点击
    hand_y = window.height - window.TILE_HEIGHT - window.HAND_MARGIN
    game_click_pos = (window.width//2, hand_y)  # 手牌区域位置
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": game_click_pos})
    pygame.event.post(event)
    window.handle_events()
    
    pygame.quit()

def test_keyboard_handling():
    """测试键盘事件处理"""
    pygame.init()
    window = GameWindow(800, 600)
    window.initialize()  # 创建游戏实例
    
    # 测试ESC键返回主菜单
    event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
    pygame.event.post(event)
    window.handle_events()
    assert window.game is None
    
    # 测试空格键跳过操作
    window.initialize()
    window.game.set_state(GameState.PLAYING)
    event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
    pygame.event.post(event)
    window.handle_events()
    
    pygame.quit()

def test_button_click_handling():
    """测试按钮点击处理"""
    pygame.init()
    window = GameWindow(800, 600)
    window.initialize()
    window.game.set_state(GameState.PLAYING)
    
    # 测试跳过按钮点击
    skip_button_pos = (750, 575)  # 跳过按钮位置
    
    pygame.quit()
  