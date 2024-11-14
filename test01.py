from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.meld import Meld

from src.core.tile import Tile, TileSuit
from src.core.yaku import judger

#示例
'''calculator = HandCalculator()
tiles = TilesConverter.string_to_136_array(man='22444', pin='333567', sou='444')
in_tile = TilesConverter.string_to_136_array(sou='4')[0]
print(tiles)
print(win_tile)

result = calculator.estimate_hand_value(tiles, win_tile)
print(result.han, result.fu)
print(result.cost['main'])
print(result.yaku)
for fu_item in result.fu_details:
    print(fu_item)'''
judger = judger.YakuJudger()
calculator = HandCalculator()
tiles = TilesConverter.string_to_136_array(man='11222234', pin='234', sou='234')
win_tile = TilesConverter.string_to_136_array(man='2')[0]
print(tiles)
print(win_tile)

config = HandConfig(
    is_tsumo=True,
    is_riichi=True,
)

dora_indicators = TilesConverter.string_to_136_array(sou='4')  # 宝牌指示牌
uradora_indicators = TilesConverter.string_to_136_array(sou='3')  # 里宝牌指示牌

result = calculator.estimate_hand_value(tiles, win_tile, [], config)
# 正确的输出方式
if result.error is None:
    print(f"和牌点数: {result.cost}")
    print(f"役种列表:")
    for yaku in result.yaku:
        print(f"{yaku.name} {yaku.han} 番")
    print(f"宝牌数: {result.han}")  # 使用 han 来获取番数
    if hasattr(result, 'dora'):  # 检查是否有 dora 属性
        print(f"宝牌: {result.dora}")
else:
    print(f"错误: {result.error}")  

print(result.han, result.fu)
print(result.cost['main'])
print(result.yaku)
for fu_item in result.fu_details:
    print(fu_item)

# # 自摸
# result = calculator.estimate_hand_value(tiles, win_tile, config=HandConfig(is_tsumo=True))
# print(result.han, result.fu)
# print(result.cost['main'], result.cost['additional'])
# print(result.yaku)
# for fu_item in result.fu_details:
#     print(fu_item)

# # 副露
# from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
# melds = [Meld(meld_type=Meld.PON, tiles=TilesConverter.string_to_136_array(pin='333'))]
# result = calculator.estimate_hand_value(tiles, win_tile, melds=melds, config=HandConfig(options=OptionalRules(has_open_tanyao=True)))
# print(result.han, result.fu)
# print(result.cost['main'])
# print(result.yaku)
# for fu_item in result.fu_details:
#     print(fu_item)

# # 向听数
# from mahjong.shanten import Shanten
# shanten = Shanten()
# tiles = TilesConverter.string_to_34_array(man='13569', pin='123459', sou='443')
# result = shanten.calculate_shanten(tiles)
# print(result)


# calculator = HandCalculator()
# tiles = TilesConverter.string_to_136_array(man='22444', pin='333567', sou='444')
# win_tile = TilesConverter.string_to_136_array(sou='4')[0]

# # 配置 HandConfig
# config = HandConfig(
#     is_tsumo=True,  # 自摸
#     is_riichi=True,  # 立直
#     options=OptionalRules(
#         has_open_tanyao=True  # 允许非门前清的断幺九成立
#     )
# )

# # 计算手牌得点
# result = calculator.estimate_hand_value(tiles, win_tile, config=config)
# print(result.han, result.fu)
# print(result.cost['main'])
# print(result.yaku)
# for fu_item in result.fu_details:
#     print(fu_item)