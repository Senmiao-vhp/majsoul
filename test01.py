from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.hand_calculating.hand_config import OptionalRules

calculator = HandCalculator()

# 设置手牌（使用'0'表示赤五）
tiles = TilesConverter.string_to_136_array(man='222505', pin='333567', sou='44', has_aka_dora=True)
win_tile = TilesConverter.string_to_136_array(sou='4')[0]

# 设置宝牌指示牌
dora_indicators = TilesConverter.string_to_136_array(pin='2')  # 示例：2筒作为宝牌指示牌

# 正确设置配置
config = HandConfig(               
    options=OptionalRules(
        has_open_tanyao=True,
        has_aka_dora=True,
    ),
    
)

result = calculator.estimate_hand_value(tiles, win_tile, [], dora_indicators, config)

if result.error:
    print(f"错误: {result.error}")
else:
    print(f"番数: {result.han}")
    print(f"符数: {result.fu}")
    print(f"点数: {result.cost['main']}")
    print("役种:")
    for yaku in result.yaku:
        print(f"{yaku.name}")