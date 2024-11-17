from typing import List, Optional
import random
from src.core.tile import Tile, TileSuit
from src.core.wall.dora import DoraManager


class Wall:
    def __init__(self):
        self.tiles = []  # 牌山
        self._remaining_count: int = 0
        self.dead_wall_tiles: List[Tile] = []  # 王牌区
        self.dead_wall_size: int = 14  # 王牌区大小
        self.dora_manager = DoraManager()  # 宝牌管理器
        self.initialize()
    
    def initialize(self) -> None:
        """初始化牌山"""
        self.tiles = self._create_tiles()  # 创建所有牌
        self._remaining_count = len(self.tiles)
        self.shuffle()
        self.setup_dead_wall()  # 设置王牌区
        
        # 初始化第一张宝牌指示牌
        first_dora = self.dead_wall_tiles[8]  # 第9张作为宝牌指示牌
        self.dora_manager.add_dora_indicator(first_dora)
        # 不在初始化时添加里宝牌指示牌
    
    def _create_tiles(self) -> List[Tile]:
        """创建所有牌"""
        tiles = []
        # 生成数牌
        for suit in [TileSuit.MAN, TileSuit.PIN, TileSuit.SOU]:
            for number in range(1, 10):
                for i in range(4):
                    is_red = number == 5 and i == 0  # 5万/5筒/5索中各有一张赤宝牌
                    tiles.append(Tile(suit, number, is_red))
        
        # 生成字牌
        for number in range(1, 8):
            for _ in range(4):
                tiles.append(Tile(TileSuit.HONOR, number))
                
        return tiles
    
    def shuffle(self) -> None:
        """洗牌"""
        random.shuffle(self.tiles)
    
    @property
    def remaining_count(self) -> int:
        """获取剩余牌数"""
        return self._remaining_count
    
    def draw(self) -> Optional[Tile]:
        """从牌山摸牌"""
        if not self.tiles or self._remaining_count <= 0:
            return None
        
        # 从牌山顶部摸一张牌
        tile = self.tiles.pop(0)
        self._remaining_count -= 1
        return tile
    
    def get_remaining_count(self) -> int:
        """获取剩余牌数"""
        return self._remaining_count
    
    def setup_dead_wall(self) -> None:
        """设置王牌区"""
        # 从牌山末尾取14张作为王牌
        self.dead_wall_tiles = self.tiles[-self.dead_wall_size:]
        self.tiles = self.tiles[:-self.dead_wall_size]
        
        # 更新剩余牌数
        self._remaining_count = len(self.tiles)
    
    def handle_kan_dora(self) -> None:
        """处理杠宝牌"""
        if len(self.dora_manager.dora_indicators) < 5:  # 最多5个宝牌指示牌
            self.dora_manager.add_dora_indicator()
    
    # 添加属性代理
    @property
    def dora_indicators(self) -> List[Tile]:
        return self.dora_manager.dora_indicators
    
    @property
    def uradora_indicators(self) -> List[Tile]:
        return self.dora_manager.uradora_indicators
    
    def add_dora_indicator(self) -> None:
        """添加新的宝牌指示牌"""
        if len(self.dora_indicators) >= 5:
            return
        
        # 计算下一个宝牌指示牌的位置
        # 初始位置是8，每次往后移2位
        next_index = 8 - (len(self.dora_indicators) * 2)
        if next_index >= 0 and next_index < len(self.dead_wall_tiles):
            next_indicator = self.dead_wall_tiles[next_index]
            self.dora_manager.add_dora_indicator(next_indicator)
    
    def reveal_uradora(self) -> None:
        """翻开里宝牌指示牌"""
        MAX_URADORA = 4  # 设置最大里宝牌数量为4
        
        # 检查数量限制
        if (len(self.uradora_indicators) >= len(self.dora_indicators) or 
            len(self.uradora_indicators) >= MAX_URADORA):
            return
            
        # 计算下一个里宝牌指示牌的位置
        # 初始位置是9，每次往后移2位
        next_index = 9 - (len(self.uradora_indicators) * 2)
        if next_index >= 0 and next_index < len(self.dead_wall_tiles):
            next_indicator = self.dead_wall_tiles[next_index]
            self.dora_manager.add_uradora_indicator(next_indicator)
    
    def add_uradora_indicator(self) -> None:
        """添加里宝牌指示牌"""
        if len(self.tiles) > 0 and len(self.uradora_indicators) < len(self.dora_indicators):
            self.uradora_indicators.append(self.tiles.pop())