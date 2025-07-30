# MeowMod

MeowMod是小孫孫打造的 Battle Cats 存檔修改器套件，提供方便的遊戲存檔編輯與管理功能。

## 安裝

使用 pip 安裝：

```bash
pip install MeowMod
功能特色
輕鬆編輯 Battle Cats 存檔內容

支援多版本遊戲存檔格式（英文版、日文版等）

提供命令列工具快速操作與自動備份

支援存檔的備份與還原，確保資料安全

彩色文字輸出，提升使用者體驗

快速開始
python
複製
編輯
import MeowMod

# 載入存檔資料
save_data = MeowMod.load_save_file("SAVE_DATA")

# 修改存檔內容範例（依實際功能調整）
# save_data['cats'][0] = 1  # 啟用第一隻貓咪

# 儲存修改後的存檔，並不提示直接覆蓋
MeowMod.write_save_data(save_data['save_data'], save_data['country_code'], "SAVE_DATA", prompt=False)
開發與貢獻
歡迎提出 Issues 或 Pull Requests，一起讓 MeowMod 更加完善。

聯絡方式
作者：小孫孫
Email：sun1000526@gmail.com