"""貓咪id查詢工具"""

from typing import Any, Optional

from ... import csv_handler, game_data_getter, helper
from ..levels import main_story, uncanny

TYPES = [
    "普通",
    "EX",
    "稀有",
    "激稀有",
    "超激稀有",
    "傳說稀有",
]


def get_level_cap_increase_amount(cat_base_level: int) -> int:
    """
    取得等級上限提升的數量

    參數:
        cat_base_level (int): 貓的基礎等級（30 = 29）

    回傳:
        int: 等級上限提升的數量
    """
    return max(0, cat_base_level - 29)


def get_unit_max_levels(is_jp: bool) -> Optional[tuple[list[int], list[int]]]:
    """
    取得所有貓的最大基礎等級和額外等級

    參數:
        is_jp (bool): 遊戲是否為日版

    回傳:
        tuple[list[int], list[int]]: 所有貓的最大基礎等級和額外等級
    """
    file_data = game_data_getter.get_file_latest("DataLocal", "unitbuy.csv", is_jp)
    if file_data is None:
        helper.error_text("無法取得 unitbuy.csv")
        return None
    data = helper.parse_int_list_list(csv_handler.parse_csv(file_data.decode("utf-8")))
    max_base_level = helper.copy_first_n(data, 50)
    max_plus_level = helper.copy_first_n(data, 51)
    return max_base_level, max_plus_level


def get_unit_max_level(
    data: tuple[list[int], list[int]], cat_id: int
) -> tuple[int, int]:
    """
    取得某隻貓的最大基礎等級與額外等級

    參數:
        data (tuple[list[int], list[int]]): 所有貓的最大基礎等級和額外等級
        cat_id (int): 貓ID

    回傳:
        tuple[int, int]: 指定貓的最大基礎等級與額外等級
    """
    try:
        return data[0][cat_id], data[1][cat_id]
    except IndexError:
        return 0, 0


def get_rarities(is_jp: bool) -> list[int]:
    """取得所有貓稀有度的ID"""

    file_data = game_data_getter.get_file_latest(
        "DataLocal", "unitbuy.csv", is_jp
    )
    if file_data is None:
        helper.error_text("無法取得 unitbuy.csv")
        return []
    data = helper.parse_int_list_list(csv_handler.parse_csv(file_data.decode("utf-8")))
    rarity_ids = helper.copy_first_n(data, 13)
    return rarity_ids


def get_rarity(rarity_ids: list[int], is_jp: bool) -> list[int]:
    """取得指定稀有度的所有貓ID"""

    rarities = get_rarities(is_jp)
    cat_ids: list[int] = []
    for rarity_id in rarity_ids:
        for i, rarity_val in enumerate(rarities):
            if int(rarity_val) == rarity_id:
                cat_ids.append(i)
    return cat_ids


def is_legend(cat_id: int) -> bool:
    """
    判斷貓是否為傳說稀有

    參數:
        cat_id (int): 貓ID

    回傳:
        bool: 是否為傳說稀有
    """
    legends = [
        24,
        25,
        130,
        172,
        268,
        323,
        352,
        383,
        426,
        437,
        462,
        464,
        532,
        554,
        568,
        613,
        622,
        653,
    ]
    if cat_id in legends:
        return True
    return False


def is_crazed(cat_id: int) -> bool:
    """
    判斷貓是否為狂亂貓

    參數:
        cat_id (int): 貓ID

    回傳:
        bool: 是否為狂亂貓
    """
    crazed = [
        91,
        92,
        93,
        94,
        95,
        96,
        97,
        98,
        99,
    ]
    if cat_id in crazed:
        return True
    return False


def get_max_cat_level_normal(save_stats: dict[str, Any]) -> int:
    """
    取得普通貓最大可升級等級

    參數:
        save_stats (dict[str, Any]): 存檔狀態

    回傳:
        int: 普通貓最大等級
    """
    if main_story.has_cleared_chapter(save_stats, 1):
        return 20
    return 10


def catseyes_unlocked(save_stats: dict[str, Any]) -> bool:
    """
    判斷是否已解鎖貓眼

    參數:
        save_stats (dict[str, Any]): 存檔狀態

    回傳:
        bool: 是否已解鎖
    """
    return helper.calculate_user_rank(save_stats) >= 1600


def get_max_cat_level_special(save_stats: dict[str, Any], cat_id: int) -> int:
    """
    取得特殊貓最大可升級等級

    參數:
        save_stats (dict[str, Any]): 存檔狀態
        cat_id (int): 貓ID

    回傳:
        int: 特殊貓最大等級
    """
    legend = is_legend(cat_id)
    acient_curse_clear = uncanny.is_ancient_curse_clear(save_stats)
    user_rank = helper.calculate_user_rank(save_stats)
    catseyes = catseyes_unlocked(save_stats)
    eoc_cleared_2 = main_story.has_cleared_chapter(save_stats, 1)

    if not eoc_cleared_2:
        return 10
    if user_rank < 1600:
        return 20
    if not catseyes:
        return 30
    if not acient_curse_clear and not legend:
        return 40
    if not acient_curse_clear and legend:
        return 30
    if acient_curse_clear and legend:
        return 40
    return 50


def get_max_cat_level_rare(save_stats: dict[str, Any]) -> int:
    """
    取得稀有貓最大可升級等級

    參數:
        save_stats (dict[str, Any]): 存檔狀態

    回傳:
        int: 稀有貓最大等級
    """
    user_rank = helper.calculate_user_rank(save_stats)
    catseyes = catseyes_unlocked(save_stats)
    cleared_eoc_2 = main_story.has_cleared_chapter(save_stats, 1)
    acient_curse_clear = uncanny.is_ancient_curse_clear(save_stats)

    if not cleared_eoc_2:
        return 10
    if user_rank < 900:
        return 20
    if user_rank < 1200:
        return 25
    if not catseyes:
        return 30
    if not acient_curse_clear:
        return 40
    return 50


def get_max_level_super_rare(save_stats: dict[str, Any], cat_id: int) -> int:
    """
    取得超稀有貓最大可升級等級

    參數:
        save_stats (dict[str, Any]): 存檔狀態
        cat_id (int): 貓ID

    回傳:
        int: 超稀有貓最大等級
    """
    user_rank = helper.calculate_user_rank(save_stats)
    cleared_eoc_2 = main_story.has_cleared_chapter(save_stats, 1)
    acient_curse_clear = uncanny.is_ancient_curse_clear(save_stats)
    crazed = is_crazed(cat_id)
    catseyes = catseyes_unlocked(save_stats)

    if not cleared_eoc_2:
        return 10
    if crazed and user_rank < 3600:
        return 20
    if not crazed and user_rank < 1000:
        return 20
    if crazed and user_rank < 3650:
        return 25
    if not crazed and user_rank < 1300:
        return 25
    if not catseyes:
        return 30
    if not acient_curse_clear:
        return 40
    return 50


def get_max_level_uber_rare(save_stats: dict[str, Any]) -> int:
    """
    取得激稀有貓最大可升級等級

    參數:
        save_stats (dict[str, Any]): 存檔狀態

    回傳:
        int: 激稀有貓最大等級
    """
    user_rank = helper.calculate_user_rank(save_stats)
    cleared_eoc_2 = main_story.has_cleared_chapter(save_stats, 1)
    acient_curse_clear = uncanny.is_ancient_curse_clear(save_stats)
    catseyes = catseyes_unlocked(save_stats)

    if not cleared_eoc_2:
        return 10
    if user_rank < 1100:
        return 20
    if user_rank < 1400:
        return 25
    if not catseyes:
        return 30
    if not acient_curse_clear:
        return 40
    return 50


def get_max_level_legend_rare(save_stats: dict[str, Any]) -> int:
    """
    取得傳說稀有貓最大可升級等級

    參數:
        save_stats (dict[str, Any]): 存檔狀態

    回傳:
        int: 傳說稀有貓最大等級
    """
    user_rank = helper.calculate_user_rank(save_stats)
    cleared_eoc_2 = main_story.has_cleared_chapter(save_stats, 1)
    acient_curse_clear = uncanny.is_ancient_curse_clear(save_stats)
    catseyes = catseyes_unlocked(save_stats)

    if not cleared_eoc_2:
        return 10
    if user_rank < 1110:
        return 20
    if user_rank < 1410:
        return 25
    if not catseyes:
        return 30
    if not acient_curse_clear:
        return 40
    return 50


def get_max_level(save_stats: dict[str, Any], rarity_index: int, cat_id: int) -> int:
    """
    取得貓可升級的最大等級

    參數:
        save_stats (dict[str, Any]): 存檔狀態
        rarity_index (int): 稀有度索引
        cat_id (int): 貓ID

    回傳:
        int: 最大等級
    """
    if rarity_index == 0:
        return get_max_cat_level_normal(save_stats)
    if rarity_index == 1:
        return get_max_cat_level_special(save_stats, cat_id)
    if rarity_index == 2:
        return get_max_cat_level_rare(save_stats)
    if rarity_index == 3:
        return get_max_level_super_rare(save_stats, cat_id)
    if rarity_index == 4:
        return get_max_level_uber_rare(save_stats)
    if rarity_index == 5:
        return get_max_level_legend_rare(save_stats)
    return 0
