"""處理故事模式關卡選擇的模組"""
from typing import Optional

from ... import user_input_handler, helper
from . import main_story


def select_specific_chapters() -> list[int]:
    """選擇特定章節"""

    print("你想選擇哪些章節？")
    ids = user_input_handler.select_not_inc(main_story.CHAPTERS, "clear")
    return ids


def get_option():
    """取得選項"""

    options = [
        "以關卡 ID 選擇特定關卡",
        "選擇直到某關為止的所有關卡",
        "選擇所有關卡",
    ]
    return user_input_handler.select_single(options)


def select_levels(
    chapter_id: Optional[int], forced_option: Optional[int] = None, total: int = 48
) -> list[int]:
    """選擇關卡"""

    if forced_option is None:
        choice = get_option()
    else:
        choice = forced_option
    if choice == 1:
        return select_specific_levels(chapter_id, total)
    if choice == 2:
        return select_levels_up_to(chapter_id, total)
    if choice == 3:
        return select_all(total)
    return []


def select_specific_levels(chapter_id: Optional[int], total: int) -> list[int]:
    """選擇特定關卡"""

    print("你想選擇哪些關卡？")
    if chapter_id is not None:
        helper.colored_text(
            f"章節：&{chapter_id+1}& : &{main_story.CHAPTERS[chapter_id]}&"
        )
    ids = user_input_handler.get_range_ids(
        "關卡 ID（例如 &1&=韓國、&2&=蒙古）", total
    )
    ids = helper.check_clamp(ids, total, 1, -1)
    return ids


def select_levels_up_to(chapter_id: Optional[int], total: int) -> list[int]:
    """選擇直到某一關為止的所有關卡"""

    print("你想選擇哪些關卡？")
    if chapter_id is not None:
        helper.colored_text(
            f"章節：&{chapter_id+1}& : &{main_story.CHAPTERS[chapter_id]}&"
        )
    stage_id = user_input_handler.get_int(
        f"請輸入要通過到哪一關（包含該關）（例如 &1&=通過韓國，&2&=通過韓國與蒙古，&{total}&=全通，&0&=全不通）?:"
    )
    stage_id = helper.clamp(stage_id, 1, total)
    return list(range(0, stage_id))


def select_all(total: int) -> list[int]:
    """選擇所有關卡"""

    return list(range(0, total))


def select_level_progress(
    chapter_id: Optional[int], total: int, examples: Optional[list[str]] = None
) -> int:
    """選擇關卡進度"""

    if examples is None:
        examples = [
            "韓國",
            "蒙古",
        ]

    print("你想通過到哪一關？（包含該關）")
    if chapter_id is not None:
        helper.colored_text(
            f"章節：&{chapter_id+1}& : &{main_story.CHAPTERS[chapter_id]}&"
        )
    progress = user_input_handler.get_int(
        f"請輸入要通過的關卡 ID（例如 &1&=通過 {examples[0]}，&2&=通過 {examples[0]} 與 {examples[1]}，&{total}&=全通，&0&=全不通）?:"
    )
    progress = helper.clamp(progress, 0, total)
    return progress
