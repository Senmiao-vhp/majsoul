import json
from pathlib import Path
from typing import Dict, Any

class Rules:
    def __init__(self):
        """初始化规则类"""
        self.config: Dict[str, Any] = {}
        self._load_rules()
    
    def _load_rules(self) -> None:
        """从配置文件加载规则"""
        try:
            config_path = Path(__file__).parent.parent.parent / 'assets' / 'config' / 'rule.json'
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"加载规则配置失败: {e}")
            # 使用默认配置
            self.config = {
                "tile_count": 136,
                "min_points": 1,
                "max_points": 13
            }
    
    def get_tile_count(self) -> int:
        """获取总牌数"""
        return self.config.get("tile_count", 136)
    
    def get_min_points(self) -> int:
        """获取最小点数"""
        return self.config.get("min_points", 1)
    
    def get_max_points(self) -> int:
        """获取最大点数"""
        return self.config.get("max_points", 13)
    
    def validate_points(self, points: int) -> bool:
        """验证点数是否合法"""
        return self.get_min_points() <= points <= self.get_max_points() 
    
    def get_player_count(self) -> int:
        """获取玩家数量"""
        return self.config.get("player_count", 4)
        
    def get_initial_points(self) -> int:
        """获取初始点数"""
        return self.config.get("initial_points", 25000)