from typing import List, Optional
from src.core.tile import Tile, TileSuit
from mahjong.tile import TilesConverter


class TileConverter:
    """麻将牌格式转换工具类"""
    
    @staticmethod
    def to_136_array(tiles: List[Tile], has_aka_dora: bool = False) -> List[int]:
        """将Tile对象列表转换为136格式数组
        
        Args:
            tiles: Tile对象列表
            has_aka_dora: 是否包含赤宝牌
            
        Returns:
            List[int]: 136格式的牌数组
        """
        # 按照花色分类
        man = ''
        pin = ''
        sou = ''
        honors = ''
        
        for tile in tiles:
            if tile.suit == TileSuit.MAN:
                man += str(tile.value)
            elif tile.suit == TileSuit.PIN:
                pin += str(tile.value)
            elif tile.suit == TileSuit.SOU:
                sou += str(tile.value)
            elif tile.suit == TileSuit.HONOR:
                honors += str(tile.value)
                
        # 转换为136格式
        tiles_136 = []
        if man:
            tiles_136.extend(sorted(TilesConverter.string_to_136_array(man=man, has_aka_dora=has_aka_dora)))
        if pin:
            tiles_136.extend(sorted(TilesConverter.string_to_136_array(pin=pin, has_aka_dora=has_aka_dora)))
        if sou:
            tiles_136.extend(sorted(TilesConverter.string_to_136_array(sou=sou, has_aka_dora=has_aka_dora)))
        if honors:
            tiles_136.extend(sorted(TilesConverter.string_to_136_array(honors=honors)))
            
        return tiles_136
            
