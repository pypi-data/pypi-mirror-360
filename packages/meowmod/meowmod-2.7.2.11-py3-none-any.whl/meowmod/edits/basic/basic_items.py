"""基礎道具編輯處理器"""
from typing import Any
from ... import item, managed_item


def edit_cat_food(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯貓罐頭"""

    cat_food = item.IntItem(
        name="貓罐頭",
        value=item.Int(save_stats["cat_food"]["Value"]),
        max_value=45000,
        bannable=item.Bannable(
            managed_item.ManagedItemType.CATFOOD, save_stats["inquiry_code"]
        ),
    )
    cat_food.edit()
    save_stats["cat_food"]["Value"] = cat_food.get_value()
    return save_stats


def edit_xp(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯經驗值"""

    experience = item.IntItem(
        name="XP",
        value=item.Int(save_stats["xp"]["Value"]),
        max_value=99999999,
    )
    experience.edit()
    save_stats["xp"]["Value"] = experience.get_value()
    return save_stats


def edit_normal_tickets(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯銀券"""

    normal_tickets = item.IntItem(
        name="普通票券",
        value=item.Int(save_stats["normal_tickets"]["Value"]),
        max_value=9999,
    )
    normal_tickets.edit()
    save_stats["normal_tickets"]["Value"] = normal_tickets.get_value()
    return save_stats


def edit_rare_tickets(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯稀有票券"""

    rare_tickets = item.IntItem(
        name="稀有票券",
        value=item.Int(save_stats["rare_tickets"]["Value"]),
        max_value=299,
        bannable=item.Bannable(
            inquiry_code=save_stats["inquiry_code"],
            work_around='&請不要直接修改稀有票券，請改用「普通票券最大交易進度」功能！這樣比較安全。',
            type=managed_item.ManagedItemType.RARE_TICKET,
        ),
    )
    rare_tickets.edit()
    save_stats["rare_tickets"]["Value"] = rare_tickets.get_value()
    return save_stats


def edit_platinum_tickets(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯白金票券"""

    platinum_tickets = item.IntItem(
        name="白金票券",
        value=item.Int(save_stats["platinum_tickets"]["Value"]),
        max_value=9,
        bannable=item.Bannable(
            inquiry_code=save_stats["inquiry_code"],
            work_around="&請不要直接修改白金票券，請改用白金碎片修改！10個白金碎片=1張白金票券，這樣比較安全。",
            type=managed_item.ManagedItemType.PLATINUM_TICKET,
        ),
    )
    platinum_tickets.edit()
    save_stats["platinum_tickets"]["Value"] = platinum_tickets.get_value()
    return save_stats


def edit_platinum_shards(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯白金碎片"""

    ticket_amount = save_stats["platinum_tickets"]["Value"]
    max_value = 99 - (ticket_amount * 10)
    platinum_shards = item.IntItem(
        name="白金碎片",
        value=item.Int(save_stats["platinum_shards"]["Value"]),
        max_value=max_value,
    )
    platinum_shards.edit()
    save_stats["platinum_shards"]["Value"] = platinum_shards.get_value()
    return save_stats


def edit_np(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯 NP"""

    nyanko_points = item.IntItem(
        name="NP",
        value=item.Int(save_stats["np"]["Value"]),
        max_value=9999,
    )
    nyanko_points.edit()
    save_stats["np"]["Value"] = nyanko_points.get_value()
    return save_stats


def edit_leadership(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯統帥旗"""

    leadership = item.IntItem(
        name="統帥旗",
        value=item.Int(save_stats["leadership"]["Value"]),
        max_value=9999,
    )
    leadership.edit()
    save_stats["leadership"]["Value"] = leadership.get_value()
    return save_stats


def edit_battle_items(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯戰鬥道具"""

    battle_items = item.IntItemGroup.from_lists(
        names=[
            "加速",
            "尋寶雷達",
            "富豪貓",
            "貓CPU",
            "貓工作",
            "狙擊貓",
        ],
        values=save_stats["battle_items"],
        maxes=9999,
        group_name="戰鬥道具",
    )
    battle_items.edit()
    save_stats["battle_items"] = battle_items.get_values()

    return save_stats


def edit_engineers(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯小幫手工程師"""

    engineers = item.IntItem(
        name="小幫手工程師",
        value=item.Int(save_stats["engineers"]["Value"]),
        max_value=5,
    )
    engineers.edit()
    save_stats["engineers"]["Value"] = engineers.get_value()
    return save_stats


def edit_catamins(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯喵力達"""

    catamins = item.IntItemGroup.from_lists(
        names=[
            "喵力達 A",
            "喵力達 B",
            "喵力達 C",
        ],
        values=save_stats["catamins"],
        maxes=9999,
        group_name="喵力達",
    )
    catamins.edit()
    save_stats["catamins"] = catamins.get_values()
    return save_stats


def edit_inquiry_code(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯詢問碼"""

    print(
        "警告：只有在知道自己在做什麼時才編輯詢問碼！錯誤編輯會導致遊戲中 elsewhere 錯誤！"
    )
    inquiry_code = item.StrItem(
        name="詢問碼",
        value=save_stats["inquiry_code"],
    )
    inquiry_code.edit()
    save_stats["inquiry_code"] = inquiry_code.get_value()
    return save_stats


def edit_rare_gacha_seed(save_stats: dict[str, Any]) -> dict[str, Any]:
    """抽獎種子"""

    rare_gacha_seed = item.IntItem(
        name="抽獎種子",
        value=item.Int(save_stats["rare_gacha_seed"]["Value"], signed=False),
        max_value=None,
    )
    rare_gacha_seed.edit()
    save_stats["rare_gacha_seed"]["Value"] = rare_gacha_seed.get_value()
    return save_stats


def edit_unlocked_slots(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯已解鎖槽位數量"""

    unlocked_slots = item.IntItem(
        name="已解鎖槽位",
        value=item.Int(save_stats["unlocked_slots"]["Value"]),
        max_value=len(save_stats["slot_names"]),
    )
    unlocked_slots.edit()
    save_stats["unlocked_slots"]["Value"] = unlocked_slots.get_value()
    return save_stats


def edit_token(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯密碼刷新令牌（Token）"""

    print(
        "警告：只有在知道自己在做什麼時才編輯 Token！錯誤編輯會導致遊戲中 elsewhere 錯誤！"
    )
    token = item.StrItem(
        name="Token",
        value=save_stats["token"],
    )
    token.edit()
    save_stats["token"] = token.get_value()
    return save_stats


def edit_restart_pack(save_stats: dict[str, Any]) -> dict[str, Any]:
    """給予重啟包"""

    save_stats["restart_pack"]["Value"] = 1
    print("成功給予重啟包")
    return save_stats


def edit_challenge_battle(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯挑戰戰鬥分數"""

    challenge_battle = item.IntItem(
        name="挑戰戰鬥",
        value=item.Int(save_stats["challenge"]["Score"]["Value"]),
        max_value=None,
    )
    challenge_battle.edit()
    save_stats["challenge"]["Score"]["Value"] = challenge_battle.get_value()
    save_stats["challenge"]["Cleared"]["Value"] = 1
    return save_stats


def edit_legend_tickets(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯傳說券"""

    legend_tickets = item.IntItem(
        name="傳說券",
        value=item.Int(save_stats["legend_tickets"]["Value"]),
        max_value=4,
        bannable=item.Bannable(
            inquiry_code=save_stats["inquiry_code"],
            type=managed_item.ManagedItemType.LEGEND_TICKET,
        ),
    )
    legend_tickets.edit()
    save_stats["legend_tickets"]["Value"] = legend_tickets.get_value()
    return save_stats


def edit_dojo_score(save_stats: dict[str, Any]) -> dict[str, Any]:
    """編輯道場分數"""

    if not save_stats["dojo_data"]:
        save_stats["dojo_data"] = {0: {0: 0}}

    dojo_score = item.IntItem(
        name="道場分數",
        value=item.Int(save_stats["dojo_data"][0][0]),
        max_value=None,
    )
    dojo_score.edit()
    save_stats["dojo_data"][0][0] = dojo_score.get_value()
    return save_stats
