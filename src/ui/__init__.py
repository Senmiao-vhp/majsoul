from typing import Optional, Tuple, Dict
import pygame

from src.core.player import Player
from ..core.game import Game
from ..core.game.state import GameState
from ..ui.renderer import GameRenderer

class GameWindow:
    """游戏主窗口类"""
    
    def __init__(self, width: int = 1280, height: int = 720):
        """初始化游戏窗口
        
        Args:
            width: 窗口宽度
            height: 窗口高度
        """
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Majsoul")
        
        # 布局常量
        self.TILE_WIDTH = 40
        self.TILE_HEIGHT = 56
        self.TILE_SPACING = 2
        self.HAND_MARGIN = 20
        
        # 游戏实例
        self.game: Optional[Game] = None
        
        # 基础颜色定义
        self.colors = {
            "background": (40, 120, 80),  # 深绿色背景
            "text": (255, 255, 255),      # 白色文字
            "button": (60, 140, 100),     # 按钮颜色
            "button_hover": (80, 160, 120) # 按钮悬停颜色
        }
        
        # 初始化字体
        self.fonts = {
            "title": pygame.font.Font(None, 64),
            "normal": pygame.font.Font(None, 32)
        }
        
        self.renderer = GameRenderer(self.screen)
        
    def initialize(self) -> None:
        """初始化游戏"""
        self.game = Game()
        
    def handle_events(self) -> bool:
        """处理事件
        
        Returns:
            bool: 是否继续运行
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                self._handle_key_press(event.key)
                
        return True
        
    def update(self) -> None:
        """更新游戏状态"""
        if self.game:
            self.game.update()
            
    def render(self) -> None:
        """渲染游戏画面"""
        if not self.game:
            self._render_main_menu()
        else:
            self.renderer.render_game(self.game)
        pygame.display.flip()
        
    def _render_main_menu(self) -> None:
        """渲染主菜单"""
        # 渲染标题
        title = self.fonts["title"].render("Majsoul", True, self.colors["text"])
        title_rect = title.get_rect(center=(self.width//2, self.height//3))
        self.screen.blit(title, title_rect)
        
        # 渲染开始按钮
        start_text = self.fonts["normal"].render("开始游戏", True, self.colors["text"])
        start_rect = start_text.get_rect(center=(self.width//2, self.height//2))
        self.screen.blit(start_text, start_rect)
        
    def _render_game(self) -> None:
        """渲染游戏画面"""
        if not self.game:
            return
            
        # 根据游戏状态渲染不同画面
        if self.game.get_state() == GameState.WAITING:
            self._render_waiting()
        elif self.game.get_state() == GameState.PLAYING:
            self._render_playing()
        elif self.game.get_state() == GameState.FINISHED:
            self._render_finished()
            
    def _handle_mouse_click(self, pos: Tuple[int, int]) -> None:
        """处理鼠标点击事件
        
        Args:
            pos: 点击位置(x, y)
        """
        if not self.game:
            # 主菜单点击处理
            self._handle_menu_click(pos)
        else:
            # 游戏内点击处理
            self._handle_game_click(pos)

    def _handle_menu_click(self, pos: Tuple[int, int]) -> None:
        """处理主菜单点击
        
        Args:
            pos: 点击位置(x, y)
        """
        # 检查开始按钮点击
        start_rect = pygame.Rect(self.width//2 - 50, self.height//2 - 20, 100, 40)
        if start_rect.collidepoint(pos):
            self.initialize()
            self.game.start()

    def _handle_game_click(self, pos: Tuple[int, int]) -> None:
        """处理游戏内点击
        
        Args:
            pos: 点击位置(x, y)
        """
        if not self.game:
            return
        
        # 检查手牌点击
        self._handle_hand_click(pos)
        # 检查操作按钮点击
        self._handle_button_click(pos)

    def _handle_key_press(self, key: int) -> None:
        """处理键盘按键事件
        
        Args:
            key: 按键值
        """
        if not self.game:
            return
        
        if key == pygame.K_ESCAPE:
            # ESC键返回主菜单
            self.game = None
        elif key == pygame.K_SPACE:
            # 空格键跳过当前操作
            if self.game.get_state() == GameState.PLAYING:
                self.game.skip_current_action()

    def _render_waiting(self) -> None:
        """渲染等待画面"""
        text = self.fonts["normal"].render("等待游戏开始...", True, self.colors["text"])
        rect = text.get_rect(center=(self.width//2, self.height//2))
        self.screen.blit(text, rect)
        
    def _render_playing(self) -> None:
        """渲染对局画面"""
        # TODO: 实现对局界面渲染
        pass
        
    def _render_finished(self) -> None:
        """渲染结束画面"""
        text = self.fonts["normal"].render("游戏结束", True, self.colors["text"])
        rect = text.get_rect(center=(self.width//2, self.height//2))
        self.screen.blit(text, rect) 

    def _handle_hand_click(self, pos: Tuple[int, int]) -> None:
        """处理手牌点击
        
        Args:
            pos: 点击位置(x, y)
        """
        if not self.game or not self.game.table:
            return
        
        current_player = self.game.table.get_current_player()
        if not current_player:
            return
        
        # 计算手牌区域
        hand_area = self._get_hand_area(current_player)
        if not hand_area.collidepoint(pos):
            return
        
        # 计算点击的是哪张牌
        tile_index = self._get_clicked_tile_index(pos, current_player)
        if tile_index is not None:
            self.game.handle_tile_click(tile_index)

    def _get_hand_area(self, player: Player) -> pygame.Rect:
        """获取手牌区域
        
        Args:
            player: 玩家对象
        
        Returns:
            pygame.Rect: 手牌区域矩形
        """
        tiles_width = len(player.hand.tiles) * (self.TILE_WIDTH + self.TILE_SPACING)
        x = (self.width - tiles_width) // 2
        y = self.height - self.TILE_HEIGHT - self.HAND_MARGIN
        return pygame.Rect(x, y, tiles_width, self.TILE_HEIGHT)

    def _get_clicked_tile_index(self, pos: Tuple[int, int], player: Player) -> Optional[int]:
        """获取点击的手牌索引
        
        Args:
            pos: 点击位置
            player: 玩家对象
        
        Returns:
            Optional[int]: 牌的索引，如果未点中则返回None
        """
        hand_area = self._get_hand_area(player)
        if not hand_area.collidepoint(pos):
            return None
        
        relative_x = pos[0] - hand_area.x
        index = relative_x // (self.TILE_WIDTH + self.TILE_SPACING)
        
        if 0 <= index < len(player.hand.tiles):
            return index
        return None 

    def _handle_button_click(self, pos: Tuple[int, int]) -> None:
        """处理操作按钮点击
        
        Args:
            pos: 点击位置(x, y)
        """
        if not self.game:
            return
        
        # 检查跳过按钮
        skip_rect = pygame.Rect(self.width - 100, self.height - 50, 80, 30)
        if skip_rect.collidepoint(pos):
            self.game.skip_current_action() 