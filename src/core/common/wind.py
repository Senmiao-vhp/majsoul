from enum import IntEnum

class Wind(IntEnum):
    """风位
    对应mahjong.tile.constants中的风位常量:
    EAST = 27
    SOUTH = 28
    WEST = 29
    NORTH = 30
    """
    EAST = 27
    SOUTH = 28
    WEST = 29
    NORTH = 30

    @property
    def chinese_name(self) -> str:
        """返回中文名称"""
        return {
            Wind.EAST: "东",
            Wind.SOUTH: "南",
            Wind.WEST: "西",
            Wind.NORTH: "北"
        }[self] 