from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.meld import Meld

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

calculator = HandCalculator()
tiles = TilesConverter.string_to_136_array(man='11223344556677')
win_tile = TilesConverter.string_to_136_array(man='7')[0]
print(tiles)
print(win_tile)
result = calculator.estimate_hand_value(tiles, win_tile)
print(result.han, result.fu)
print(result.cost['main'])
print(result.yaku)
for fu_item in result.fu_details:
    print(fu_item)

# 自摸
result = calculator.estimate_hand_value(tiles, win_tile, config=HandConfig(is_tsumo=True))
print(result.han, result.fu)
print(result.cost['main'], result.cost['additional'])
print(result.yaku)
for fu_item in result.fu_details:
    print(fu_item)

# 副露
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
melds = [Meld(meld_type=Meld.PON, tiles=TilesConverter.string_to_136_array(pin='333'))]
result = calculator.estimate_hand_value(tiles, win_tile, melds=melds, config=HandConfig(options=OptionalRules(has_open_tanyao=True)))
print(result.han, result.fu)
print(result.cost['main'])
print(result.yaku)
for fu_item in result.fu_details:
    print(fu_item)

# 向听数
from mahjong.shanten import Shanten
shanten = Shanten()
tiles = TilesConverter.string_to_34_array(man='13569', pin='123459', sou='443')
result = shanten.calculate_shanten(tiles)
print(result)


calculator = HandCalculator()
tiles = TilesConverter.string_to_136_array(man='22444', pin='333567', sou='444')
win_tile = TilesConverter.string_to_136_array(sou='4')[0]

# 配置 HandConfig
config = HandConfig(
    is_tsumo=True,  # 自摸
    is_riichi=True,  # 立直
    options=OptionalRules(
        has_open_tanyao=True  # 允许非门前清的断幺九成立
    )
)

# 计算手牌得点
result = calculator.estimate_hand_value(tiles, win_tile, config=config)
print(result.han, result.fu)
print(result.cost['main'])
print(result.yaku)
for fu_item in result.fu_details:
    print(fu_item)