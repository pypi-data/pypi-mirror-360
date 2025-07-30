from typing import Any, Union

from . import (
    helper,
    user_input_handler,
    config_manager,
)
from .edits import basic, cats, gamototo, levels, other, save_management


def fix_elsewhere_old(save_stats: dict[str, Any]) -> dict[str, Any]:
    """使用兩個存檔檔案修正 elsewhere 錯誤"""
    main_token = save_stats["token"]
    main_iq = save_stats["inquiry_code"]
    input("請選擇一個目前遊戲中載入且沒有 elsewhere 錯誤且未被封鎖的存檔\n按 Enter 繼續：")
    new_path = helper.select_file(
        "選擇一個乾淨的存檔檔案",
        helper.get_save_file_filetype(),
        helper.get_save_path(),
    )
    if not new_path:
        print("請選擇一個存檔檔案")
        return save_stats

    data = helper.load_save_file(new_path)
    new_stats = data["save_stats"]
    new_token = new_stats["token"]
    new_iq = new_stats["inquiry_code"]
    save_stats["token"] = new_token
    save_stats["inquiry_code"] = new_iq

    helper.colored_text(f"已替換查詢碼：&{main_iq}& 為 &{new_iq}&")
    helper.colored_text(f"已替換 Token：&{main_token}& 為 &{new_token}&")
    return save_stats


FEATURES: dict[str, Any] = {
    "存檔管理": {
        "保存存檔": save_management.save.save_save,
        "保存變更並上傳至遊戲伺服器（取得轉移碼和確認碼）": save_management.server_upload.save_and_upload,
        "保存變更至檔案": save_management.save.save,
        "保存變更並用 adb 推送存檔（不重新開啟遊戲）": save_management.save.save_and_push,
        "保存變更並用 adb 推送存檔（重新開啟遊戲）": save_management.save.save_and_push_rerun,
        "匯出存檔資料為 json": save_management.other.export,
        "用 adb 清除存檔資料（用於產生新帳號且不重新安裝遊戲）": save_management.other.clear_data,
        "上傳可封鎖物品追蹤資料（儲存或退出時自動執行）": save_management.server_upload.upload_metadata,
        "載入存檔資料": save_management.load.select,
        "轉換存檔資料版本": save_management.convert.convert_save,
    },
    "道具": {
        "貓罐頭": basic.basic_items.edit_cat_food,
        "XP": basic.basic_items.edit_xp,
        "貓咪券": {
            "銀券": basic.basic_items.edit_normal_tickets,
            "稀有券": basic.basic_items.edit_rare_tickets,
            "白金券": basic.basic_items.edit_platinum_tickets,
            "白金碎片": basic.basic_items.edit_platinum_shards,
            "傳說券": basic.basic_items.edit_legend_tickets,
        },
        "NP": basic.basic_items.edit_np,
        "統帥旗": basic.basic_items.edit_leadership,
        "戰鬥道具": basic.basic_items.edit_battle_items,
        "貓眼石": basic.catseyes.edit_catseyes,
        "貓薄荷 / 獸石": basic.catfruit.edit_catfruit,
        "本能珠珠": basic.talent_orbs_new.edit_talent_orbs,
        "喵利達": basic.basic_items.edit_catamins,
        "物品方案（允許獲得不封鎖物品）": other.scheme_item.edit_scheme_data,
    },
    "加碼 / 小幫手": {
        "小幫手工程師": basic.basic_items.edit_engineers,
        "基礎材料": basic.ototo_base_mats.edit_base_mats,
        "喵利達": basic.basic_items.edit_catamins,
        "加碼多多經驗值 / 等級": gamototo.gamatoto_xp.edit_gamatoto_xp,
        "貓咪砲": gamototo.ototo_cat_cannon.edit_cat_cannon,
        "加碼多多隊員": gamototo.helpers.edit_helpers,
        "修復加碼導致遊戲當機": gamototo.fix_gamatoto.fix_gamatoto,
    },
    "貓咪 / 特殊技能": {
        "取得 / 移除貓咪": {
            "取得貓咪": cats.get_remove_cats.get_cat,
            "移除貓咪": cats.get_remove_cats.remove_cats,
        },
        "升級貓咪": cats.upgrade_cats.upgrade_cats,
        "三階貓咪": {
            "取得貓咪三階": cats.evolve_cats.get_evolve,
            "移除貓咪三階": cats.evolve_cats.remove_evolve,
            "強制三階（無真形態者會成為空白貓）": cats.evolve_cats.get_evolve_forced,
        },
        "本能": {
            "為每隻選擇的貓咪單獨設定本能": cats.talents.edit_talents_individual,
            "全部選擇貓咪本能最大化 / 移除": cats.talents.max_all_talents,
        },
        "收集 / 移除貓咪指南": {
            "設定貓咪指南條目（不給予貓罐頭）": cats.clear_cat_guide.collect_cat_guide,
            "取消認領貓咪指南條目": cats.clear_cat_guide.remove_cat_guide,
        },
        "取得關卡掉落 - 移除提示視窗": cats.chara_drop.get_character_drops,
        "升級特殊技能 / 能力": cats.upgrade_blue.upgrade_blue,
    },
    "關卡 / 寶物": {
        "主線章節通關 / 未通關": {
            "為所有選擇章節通關所有關卡": levels.main_story.clear_all,
            "為每個選擇章節通關每個關卡": levels.main_story.clear_each,
        },
        "寶物": {
            "寶物組合（例如能量飲料、水晶等）": levels.treasures.treasure_groups,
            "特定關卡與章節單獨設定": levels.treasures.specific_stages,
            "特定關卡與所有章節同時設定": levels.treasures.specific_stages_all_chapters,
        },
        "殭屍關卡 / 爆發": levels.outbreaks.edit_outbreaks,
        "活動關卡": levels.event_stages.event_stages,
        "傳說故事": levels.event_stages.stories_of_legend,
        "神秘傳說": levels.uncanny.edit_uncanny,
        "零傳說": levels.zerolegends.edit_zl,
        "阿庫領域 / 門通關": levels.aku.edit_aku,
        "解鎖阿庫領域 / 門": levels.unlock_aku_realm.unlock_aku_realm,
        "試煉": levels.gauntlet.edit_gauntlet,
        "合作試煉": levels.gauntlet.edit_collab_gauntlet,
        "塔防": levels.towers.edit_tower,
        "巨獸狩獵": levels.behemoth_culling.edit_behemoth_culling,
        "未來計分挑戰": levels.itf_timed_scores.timed_scores,
        "挑戰戰鬥分數": basic.basic_items.edit_challenge_battle,
        "清除教學": levels.clear_tutorial.clear_tutorial,
        "貓爪道場分數（入門大殿）": basic.basic_items.edit_dojo_score,
        "新增謎題關卡": levels.enigma_stages.edit_enigma_stages,
        "允許反覆通關議會關卡": levels.allow_filibuster_clearing.allow_filibuster_clearing,
        "傳說任務": levels.legend_quest.edit_legend_quest,
    },
    "查詢碼 / Token / 帳號": {
        "查詢碼": basic.basic_items.edit_inquiry_code,
        "Token": basic.basic_items.edit_token,
        "修復 elsewhere 錯誤 / 解封帳號": other.fix_elsewhere.fix_elsewhere,
        "舊版修復 elsewhere 錯誤 / 解封帳號（需要兩個存檔）": fix_elsewhere_old,
        "生成新的查詢碼與 Token": other.create_new_account.create_new_account,
    },
    "其他": {
        "抽獎種子": basic.basic_items.edit_rare_gacha_seed,
        "解鎖裝備槽位": basic.basic_items.edit_unlocked_slots,
        "取得重啟包 / 回歸模式": basic.basic_items.edit_restart_pack,
        "喵勳章": other.meow_medals.medals,
        "遊玩時間": other.play_time.edit_play_time,
        "解鎖 / 移除敵人指南條目": other.unlock_enemy_guide.enemy_guide,
        "貓薄荷挑戰 / 任務": other.missions.edit_missions,
        "普通票券最大交易進度（允許不封鎖稀有票券）": other.trade_progress.set_trade_progress,
        "取得 / 移除黃金通行證": other.get_gold_pass.get_gold_pass,
        "領取 / 移除全部用戶等級獎勵（不給物品）": other.claim_user_rank_rewards.edit_rewards,
        "貓咪神社等級 / 經驗值": other.cat_shrine.edit_shrine_xp,
    },
    "修復": {
        "修復時間錯誤": other.fix_time_issues.fix_time_issues,
        "解鎖裝備選單": other.unlock_equip_menu.unlock_equip,
        "清除教學": levels.clear_tutorial.clear_tutorial,
        "修復 elsewhere 錯誤 / 解封帳號": other.fix_elsewhere.fix_elsewhere,
        "舊版修復 elsewhere 錯誤 / 解封帳號（需要兩個存檔）": fix_elsewhere_old,
        "修復加碼導致遊戲當機": gamototo.fix_gamatoto.fix_gamatoto,
    },
    "編輯設定": {
        "編輯語言設定": config_manager.edit_locale,
        "編輯預設國碼": config_manager.edit_default_gv,
        "編輯預設存檔路徑": config_manager.edit_default_save_file_path,
        "編輯固定存檔路徑": config_manager.edit_fixed_save_path,
        "編輯編輯器設定": config_manager.edit_editor_settings,
        "編輯啟動設定": config_manager.edit_start_up_settings,
        "編輯儲存變更設定": config_manager.edit_save_changes_settings,
        "編輯伺服器設定": config_manager.edit_server_settings,
        "編輯設定檔路徑": config_manager.edit_config_path,
    },
    "離開": helper.exit_check_changes,
}


def get_feature(
    selected_features: Any, search_string: str, results: dict[str, Any]
) -> dict[str, Any]:
    """搜尋功能名稱內含搜尋字串的功能"""

    for feature in selected_features:
        feature_data = selected_features[feature]
        if isinstance(feature_data, dict):
            feature_data = get_feature(feature_data, search_string, results)
        if search_string.lower().replace(" ", "") in feature.lower().replace(" ", ""):
            results[feature] = selected_features[feature]
    return results


def show_options(
    save_stats: dict[str, Any], features_to_use: dict[str, Any]
) -> dict[str, Any]:
    """讓使用者輸入功能編號或名稱，並取得符合的功能"""

    if (
        not config_manager.get_config_value_category("EDITOR", "SHOW_CATEGORIES")
        and FEATURES == features_to_use
    ):
        user_input = ""
    else:
        prompt = "你想編輯什麼？（有些選項內含子功能）"
        if config_manager.get_config_value_category(
            "EDITOR", "SHOW_FEATURE_SELECT_EXPLANATION"
        ):
            prompt += "\n你可以輸入編號以執行功能，或輸入關鍵字搜尋功能（例如輸入貓罐頭會執行貓罐頭功能，輸入票券會顯示所有修改票券的功能）\n直接按 Enter 可顯示所有功能列表"
        user_input = user_input_handler.colored_input(f"{prompt}：\n")
    user_int = helper.check_int(user_input)
    results = []
    if user_int is None:
        results = get_feature(features_to_use, user_input, {})
    else:
        if user_int < 1 or user_int > len(features_to_use) + 1:
            helper.colored_text("數值超出範圍", helper.RED)
            return show_options(save_stats, features_to_use)
        if FEATURES != features_to_use:
            if user_int - 2 < 0:
                return menu(save_stats)
            results = features_to_use[list(features_to_use)[user_int - 2]]
        else:
            results = features_to_use[list(features_to_use)[user_int - 1]]
    if not isinstance(results, dict):
        save_stats_return = results(save_stats)
        if save_stats_return is None:
            return save_stats
        return save_stats_return
    if len(results) == 0:
        helper.colored_text("找不到符合名稱的功能。", helper.RED)
        return menu(save_stats)
    if len(results) == 1 and isinstance(list(results.values())[0], dict):
        results = results[list(results)[0]]
    if len(results) == 1:
        save_stats_return = results[list(results)[0]](save_stats)
        if save_stats_return is None:
            return save_stats
        return save_stats_return

    helper.colored_list(["返回上一頁"] + list(results))
    return show_options(save_stats, results)


def menu(
    save_stats: dict[str, Any], path_save: Union[str, None] = None
) -> dict[str, Any]:
    """顯示選單並讓使用者選擇想編輯的功能"""

    if path_save:
        helper.set_save_path(path_save)
    if config_manager.get_config_value_category("EDITOR", "SHOW_CATEGORIES"):
        helper.colored_list(list(FEATURES))
    save_stats = show_options(save_stats, FEATURES)

    return save_stats

