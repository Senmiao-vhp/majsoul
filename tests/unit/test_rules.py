import pytest
from src.core.rules import Rules

def test_rules_init():
    """测试Rules类初始化"""
    rules = Rules()
    assert isinstance(rules.config, dict)
    assert rules.get_tile_count() == 136

def test_validate_points():
    """测试点数验证"""
    rules = Rules()
    assert rules.validate_points(1) is True
    assert rules.validate_points(13) is True
    assert rules.validate_points(0) is False
    assert rules.validate_points(14) is False