from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.hand_calculating.hand_config import OptionalRules
from mahjong.meld import Meld
from mahjong.constants import EAST, SOUTH, WEST, NORTH, HAKU, HATSU, CHUN

def test_minkan_patterns():
    """测试杠和牌型"""
    calculator = HandCalculator()
    
    # 和牌型
    tiles = TilesConverter.string_to_136_array(man='234', pin='234', sou='99', honors='111222')
    win_tile = TilesConverter.string_to_136_array(man='2')[0]
    # minkan = Meld(
    #     meld_type=Meld.KAN,
    #     tiles=TilesConverter.string_to_136_array(pin='2222'),
    #     opened=True,
    # )
    # chi = Meld(
    #     meld_type=Meld.CHI,
    #     tiles=TilesConverter.string_to_136_array(pin='345'),
    #     opened=False,
    #     who=0,
    #     from_who=1,
    #     called_tile=TilesConverter.string_to_136_array(pin='3')[0]
    # )
    # pon = Meld(
    #     meld_type=Meld.PON,
    #     tiles=TilesConverter.string_to_136_array(sou='777'),
    #     opened=True,
    # )
    
    config = HandConfig(
        player_wind=EAST,  # 东家
        round_wind=SOUTH,  # 南场
        options=OptionalRules(
            has_open_tanyao=True,
            has_aka_dora=True,
        ),
    )
    
    # 测试每种牌型
    print("\n=== 测试牌型 ===")
    result = calculator.estimate_hand_value(tiles, win_tile, None, None, config)
    print_result(result)


def print_result(result):
    """打印结果"""
    if result.error:
        print(f"错误: {result.error}")
        if result.error == HandCalculator.ERR_HAND_NOT_WINNING:
            print("错误原因: 不是有效的和牌型")
        elif result.error == HandCalculator.ERR_NO_YAKU:
            print("错误原因: 无役")
        elif result.error == HandCalculator.ERR_NO_WINNING_TILE:
            print("错误原因: 和牌张不在手牌中")
        elif result.error == HandCalculator.ERR_HAND_NOT_CORRECT:
            print("错误原因: 手牌结构不正确")
    else:
        print(f"番数: {result.han}")
        print(f"符数: {result.fu}")
        print(f"点数: {result.cost['main']}")
        print("役种:")
        for yaku in result.yaku:
            print(f"{yaku.name}")
        print("\n符数详情:")
        for fu_item in result.fu_details:
            print(f"{fu_item}")

if __name__ == "__main__":
    test_minkan_patterns()