import pytest
import pygame

def test_pygame_init():
    """测试Pygame初始化"""
    pygame.init()
    assert pygame.get_init() is True
    pygame.quit()

def test_pygame_display():
    """测试Pygame显示功能"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    assert pygame.display.get_surface() is not None
    
    # 测试基本绘制
    screen.fill((255, 255, 255))
    pygame.display.flip()
    
    pygame.quit()

def test_pygame_event():
    """测试Pygame事件系统"""
    pygame.init()
    pygame.display.set_mode((800, 600))
    
    # 清空事件队列
    pygame.event.clear()
    
    # 生成一个测试事件
    test_event = pygame.event.Event(pygame.QUIT)
    pygame.event.post(test_event)
    
    # 获取所有事件并检查是否包含QUIT事件
    events = pygame.event.get()
    assert any(event.type == pygame.QUIT for event in events)
    
    pygame.quit() 