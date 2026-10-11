# 來源與修改紀錄

本發布包名稱為 **M4 Image Studio**，使用 Qwen-Image 2.1 模型，屬於社群整理版本。

程式衍生自 [Sanket Rajendra Shinde 的 qwen-image-studio](https://github.com/sanketshinde3001/qwen-image-studio)，來源版本為 `b5cf4c0`。原作者的 MIT 授權與著作權聲明完整保留於 [LICENSE](LICENSE)。

這次整理的修改包含：

- 在原 Web UI 加入獨立的 Turbo 8-step preset，支援文字生圖及圖片編輯，固定官方的 8-step sigma grid。
- 分開使用原 4-step 與新 Turbo 8-step 的 native engine；保留 queue、gallery、upload、edit、mask 和 outputs 流程。
- 加入 macOS／Apple Silicon／Python 環境檢查、完整安裝入口與 Finder 雙擊入口。
- 固定模型與原生程式下載來源，核對 SHA-256；加入安裝與推論參數的回歸檢查。
- 修正既有命令列腳本在引擎失敗後仍顯示已儲存的問題；保留其模型與採樣設定。
- 加入繁體中文安裝、自測及 GitHub 上傳教學；公開展示名稱改為 M4 Image Studio。

本包只包含控制程式、教學與測試。模型權重、原生程式、使用者圖片與本機設定均不隨包散布；安裝時從各自發布來源下載。

## 模型與其他元件

程式碼的 MIT 授權不替代下載元件的授權。來源與授權連結見 [MODEL_SOURCES.md](MODEL_SOURCES.md)。Qwen-Image 2.1、Turbo 與 Fun-Acc 模型來源使用 Qwen Research License；該文件限定研究／評估用途，商業使用需另取得授權。

Qwen is licensed under the Qwen RESEARCH LICENSE AGREEMENT, Copyright (c) 2026 Hangzhou Tongyi Laboratory Technology Co., Ltd. All Rights Reserved.

下載元件來源：Qwen／Tongyi Laboratory、Alibaba PAI／VideoX-Fun、Unsloth、eastmoe、AtomicChat、stable-diffusion.cpp、llama.cpp、Real-ESRGAN。各自保有其著作權與授權。
