from typing import List, Optional, Union, Dict
from collections import Counter
from ..tile import Tile, TileSuit

class Hand:
    def __init__(self):
        """初始化手牌"""
        self.tiles: List[Tile] = []
        self.melds: List[List[Tile]] = []  # 副露
        self.waiting_tiles: List[Tile] = []  # 听牌列表
        
    def add_tile(self, tile: Tile) -> None:
        """添加一张牌"""
        self.tiles.append(tile)
        self._sort_tiles()
        
    def discard_tile(self, tile_or_index: Union[Tile, int]) -> Optional[Tile]:
        """打出一张牌
        Args:
            tile_or_index: 可以是Tile对象或者索引
        Returns:
            打出的牌，如果失败返回None
        """
        if isinstance(tile_or_index, int):
            if 0 <= tile_or_index < len(self.tiles):
                return self.tiles.pop(tile_or_index)
        elif isinstance(tile_or_index, Tile):
            if tile_or_index in self.tiles:
                self.tiles.remove(tile_or_index)
                return tile_or_index
        return None
        
    def _sort_tiles(self) -> None:
        """整理手牌"""
        self.tiles.sort(key=lambda x: (x.suit.value, x.value))
        
    def add_meld(self, tiles: List[Tile]) -> None:
        """添加一组副露"""
        if len(tiles) >= 3:  # 副露至少需要3张牌
            self.melds.append(tiles)
            self._sort_tiles()
        
    def get_melds(self) -> List[List[Tile]]:
        """获取所有副露"""
        return self.melds
        
    def check_win(self, new_tile: Optional[Tile] = None) -> bool:
        """检查是否和牌"""
        # 复制手牌进行检查
        test_tiles = self.tiles.copy()
        if new_tile:
            test_tiles.append(new_tile)
            
        # 检查牌数是否正确
        if len(test_tiles) != 14:
            return False
            
        # 排序手牌
        test_tiles.sort()
        
        # 检查特殊和牌型
        if self._check_seven_pairs(test_tiles):
            return True
            
        if self._check_thirteen_orphans(test_tiles):
            return True
            
        # 检查普通和牌型
        return self._check_normal_win(test_tiles)
        
    def _check_seven_pairs(self, tiles: List[Tile]) -> bool:
        """检查七对和牌"""
        if len(tiles) != 14:
            return False
            
        # 使用Counter来统计每种牌的数量
        tile_str_counts = Counter(str(tile) for tile in tiles)
        # 检查是否恰好有7个对子
        return all(count == 2 for count in tile_str_counts.values()) and len(tile_str_counts) == 7
        
    def _check_thirteen_orphans(self, tiles: List[Tile]) -> bool:
        """检查国士无双和牌"""
        if len(tiles) != 14:
            return False
            
        # 幺九牌列表
        terminals = [
            Tile(TileSuit.CHARACTERS, 1), Tile(TileSuit.CHARACTERS, 9),
            Tile(TileSuit.CIRCLES, 1), Tile(TileSuit.CIRCLES, 9),
            Tile(TileSuit.BAMBOO, 1), Tile(TileSuit.BAMBOO, 9),
            # 字牌
            Tile(TileSuit.HONOR, 1), Tile(TileSuit.HONOR, 2),
            Tile(TileSuit.HONOR, 3), Tile(TileSuit.HONOR, 4),
            Tile(TileSuit.HONOR, 5), Tile(TileSuit.HONOR, 6),
            Tile(TileSuit.HONOR, 7)
        ]
        
        # 使用Counter统计牌的数量
        tile_str_counts = Counter(str(tile) for tile in tiles)
        # 检查是否包含所有幺九牌
        return all(str(tile) in tile_str_counts for tile in terminals)
        
    def _check_normal_win(self, tiles: List[Tile]) -> bool:
        """检查普通和牌型"""
        if len(tiles) != 14:
            return False
            
        # 排序手牌
        tiles.sort()
        
        # 检查雀头
        for i in range(len(tiles) - 1):
            if tiles[i] == tiles[i + 1]:
                # 复制剩余牌进行检查
                remaining = tiles.copy()
                # 移除雀头
                remaining.pop(i + 1)
                remaining.pop(i)
                # 检查剩余牌是否可以组成面子
                if self._check_mentsu(remaining):
                    return True
        return False
        
    def _check_mentsu(self, tiles: List[Tile]) -> bool:
        """检查剩余牌是否可以组成面子"""
        if not tiles:
            return True
            
        # 排序手牌
        tiles.sort()
        
        # 1. 尝试刻子
        if len(tiles) >= 3 and tiles[0] == tiles[1] == tiles[2]:
            return self._check_mentsu(tiles[3:])
        
        # 2. 尝试顺子
        if len(tiles) >= 3 and tiles[0].suit in [TileSuit.CHARACTERS, TileSuit.CIRCLES, TileSuit.BAMBOO]:
            if (tiles[0].suit == tiles[1].suit == tiles[2].suit and
                tiles[1].value == tiles[0].value + 1 and
                tiles[2].value == tiles[1].value + 1):
                return self._check_mentsu(tiles[3:])
            
        # 3. 如果第一张牌无法组成面子，尝试从下一张牌开始
        if len(tiles) > 1:
            return self._check_mentsu(tiles[1:])
            
        return False
        
    def check_tenpai(self) -> List[Tile]:
        """检查听牌
        Returns:
            List[Tile]: 可能的和牌列表
        """
        waiting_tiles = []
        # 复制手牌进行测试
        test_tiles = self.tiles.copy()
        
        # 检查当前手牌是否已经有对子
        tile_counts = Counter(str(tile) for tile in test_tiles)
        pairs_count = sum(1 for count in tile_counts.values() if count == 2)
        
        # 遍历所有可能的牌
        for suit in TileSuit:
            for value in range(1, 10):
                if suit == TileSuit.HONOR and value > 7:
                    continue
                    
                test_tile = Tile(suit, value)
                # 添加测试牌
                test_tiles.append(test_tile)
                # 检查是否和牌
                if self.check_win(test_tile):
                    # 对于七对子听牌，只有一种可能
                    if pairs_count == 6:
                        # 检查是否是七对子和牌
                        if self._check_seven_pairs(test_tiles):
                            waiting_tiles = [test_tile]
                            break
                    else:
                        waiting_tiles.append(test_tile)
                # 移除测试牌
                test_tiles.remove(test_tile)
                
        self.waiting_tiles = waiting_tiles
        return waiting_tiles
        
    def is_tenpai(self) -> bool:
        """检查是否听牌"""
        return len(self.check_tenpai()) > 0