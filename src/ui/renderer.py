from typing import Dict, List, Optional, Tuple
import pygame
from ..core.game import Game
from ..core.player import Player
from ..core.tile import Tile

class GameRenderer:
    """游戏渲染器"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # 颜色定义
        self.colors = {
            "table": (40, 120, 80),    # 牌桌绿色
            "tile": (255, 255, 255),   # 牌面白色
            "text": (255, 255, 255),   # 文字白色
            "highlight": (255, 255, 0), # 高亮黄色
            "count": (200, 200, 200)    # 牌数显示灰色
        }
        
        # 布局常量
        self.TILE_WIDTH = 40
        self.TILE_HEIGHT = 56
        self.TILE_SPACING = 2
        self.HAND_MARGIN = 20
        
        # 字体初始化
        self.fonts = {
            "small": pygame.font.Font(None, 24),
            "normal": pygame.font.Font(None, 32),
            "large": pygame.font.Font(None, 48)
        }
        
    def render_game(self, game: Game) -> None:
        """渲染游戏画面"""
        # 清空屏幕
        self.screen.fill(self.colors["table"])
        
        if not game:
            return
            
        # 渲染玩家手牌
        self._render_hands(game)
        
        # 渲染打的牌
        self._render_discards(game)
        
        # 渲染剩余牌数
        self._render_wall_count(game)
        
        # 渲染当前玩家标记
        self._render_current_player(game)
        
    def _render_hands(self, game: Game) -> None:
        """渲染所有玩家手牌"""
        for i, player in enumerate(game.players):
            # 计算手牌区域位置
            if i == 0:  # 下方玩家(自己)
                x = (self.width - len(player.hand.tiles) * (self.TILE_WIDTH + self.TILE_SPACING)) // 2
                y = self.height - self.TILE_HEIGHT - self.HAND_MARGIN
                self._render_hand(player, x, y, False)
            elif i == 1:  # 右方玩家
                x = self.width - self.TILE_HEIGHT - self.HAND_MARGIN
                
    def _render_hand(self, player: Player, x: int, y: int, is_vertical: bool) -> None:
        """渲染单个玩家的手牌
        
        Args:
            player: 玩家对象
            x: 起始x坐标
            y: 起始y坐标
            is_vertical: 是否垂直显示
        """
        for i, tile in enumerate(player.hand.tiles):
            tile_x = x + (self.TILE_WIDTH + self.TILE_SPACING) * i if not is_vertical else x
            tile_y = y if not is_vertical else y + (self.TILE_HEIGHT + self.TILE_SPACING) * i
            self._render_tile(tile, tile_x, tile_y, is_vertical)

    def _render_discards(self, game: Game) -> None:
        """渲染打出的牌区域"""
        if not game.table:
            return
        
        # 每个玩家的打牌区域位置和大小
        discard_areas = {
            0: (self.width//2 - 200, self.height - 200, 400, 120),  # 下方
            1: (self.width - 120, self.height//2 - 200, 100, 400),  # 右方
            2: (self.width//2 - 200, 80, 400, 120),                 # 上方
            3: (20, self.height//2 - 200, 100, 400)                 # 左方
        }
        
        # 渲染每个玩家的打出牌
        for i, player in enumerate(game.table.players):
            if not hasattr(player, 'discards'):
                continue
            
            area = discard_areas[i]
            is_vertical = i in (1, 3)  # 右侧和左侧玩家的牌垂直显示
            
            # 计算每张牌的位置
            tiles_per_row = 6 if is_vertical else 12
            spacing = 2
            tile_width = self.TILE_WIDTH if not is_vertical else self.TILE_HEIGHT
            tile_height = self.TILE_HEIGHT if not is_vertical else self.TILE_WIDTH
            
            for j, tile in enumerate(player.discards):
                row = j // tiles_per_row
                col = j % tiles_per_row
                
                if is_vertical:
                    x = area[0]
                    y = area[1] + (tile_height + spacing) * col + (area[3] // tiles_per_row) * row
                else:
                    x = area[0] + (tile_width + spacing) * col + (area[2] // tiles_per_row) * row
                    y = area[1]
                
                # 渲染牌面
                self._render_tile(tile, x, y, is_vertical)
                
                # 如果是最后打出的牌，添加高亮效果
                if j == len(player.discards) - 1:
                    rect = pygame.Rect(x, y, tile_width, tile_height)
                    pygame.draw.rect(self.screen, self.colors["highlight"], rect, 2)

    def _render_wall_count(self, game: Game) -> None:
        """渲染剩余牌数"""
        if not game.table or not game.table.wall:
            return
        
        remaining = game.table.wall.get_remaining_count()
        text = self.fonts["normal"].render(
            f"剩余: {remaining}",
            True, 
            self.colors["count"]
        )
        
        # 显示在左上角
        rect = text.get_rect()
        rect.topleft = (10, 10)
        self.screen.blit(text, rect)
        
        # 如果剩余牌数少于10张，使用红色显示
        if remaining < 10:
            text = self.fonts["normal"].render(
                f"剩余: {remaining}",
                True, 
                (255, 0, 0)  # 红色
            )
            self.screen.blit(text, rect)

    def _render_current_player(self, game: Game) -> None:
        """渲染当前玩家标记"""
        if not game.table:
            return
        
        current_player = game.table.get_current_player()
        if not current_player:
            return
        
        # 获取当前玩家索引
        player_index = game.table.players.index(current_player)
        
        # 计算标记位置
        mark_positions = [
            (self.width//2, self.height - 10),  # 下方
            (self.width - 10, self.height//2),   # 右方
            (self.width//2, 10),                 # 上方
            (10, self.height//2)                 # 左方
        ]
        
        # 绘制绿色圆点标记
        pos = mark_positions[player_index]
        pygame.draw.circle(self.screen, (0, 255, 0), pos, 5)

    def _render_tile(self, tile: Tile, x: int, y: int, is_vertical: bool) -> None:
        """渲染单张牌面
        
        Args:
            tile: 要渲染的牌
            x: 渲染位置x坐标
            y: 渲染位置y坐标
            is_vertical: 是否垂直显示
        """
        # 计算牌面尺寸
        width = self.TILE_HEIGHT if is_vertical else self.TILE_WIDTH
        height = self.TILE_WIDTH if is_vertical else self.TILE_HEIGHT
        
        # 绘制牌面底色
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, self.colors["tile"], rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)  # 黑色边框
        
        # 渲染牌面文字
        font = self.fonts["small"]
        text = f"{tile.suit.value}{tile.value}"
        text_surface = font.render(text, True, (0, 0, 0))
        
        # 调整文字位置
        text_rect = text_surface.get_rect()
        if is_vertical:
            text_rect.center = (x + width//2, y + height//2)
            # 旋转文字
            text_surface = pygame.transform.rotate(text_surface, 90)
        else:
            text_rect.center = (x + width//2, y + height//2)
        
        self.screen.blit(text_surface, text_rect)

    def render_special_draw(self, draw_type: str) -> None:
        """渲染特殊流局提示
        Args:
            draw_type: 流局类型
        """
        if draw_type == 'four_riichi':
            message = "四家立直"
        elif draw_type == 'four_kans':
            message = "四杠散了"
        elif draw_type == 'nine_terminals':
            message = "九种九牌"
        
        # 在屏幕中央显示提示
        x = (self.width - len(message) * self.FONT_SIZE) // 2
        y = self.height // 2
        self.screen.addstr(y, x, message)