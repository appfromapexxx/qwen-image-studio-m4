# 驗證範圍

整理日期：2026-10-11。

## 本機推論驗證

從目前安裝複製的 Web UI 推論程式已完成以下流程：

| 模式 | 操作 | 結果 |
|---|---|---|
| 原 4-step Turbo | 512×512 文字生圖 | 完成，原 base model 與 Fun-Acc LoRA 路徑保留 |
| Turbo 8-step | 512×512 文字生圖 | 完成，產生指定尺寸 PNG |
| Turbo 8-step | 768×768 文字生圖 | 完成，產生指定尺寸 PNG |
| Turbo 8-step | 768×768 圖片編輯 | 完成，透過原上傳流程將紅色茶壺改為藍色 |

三項 Turbo 8-step 工作的設定紀錄均為 `preset=turbo8`、8 步、CFG 1、Euler、`Qwen-Image-2.1-Turbo-AD-Q4_K.gguf` 與官方固定 sigma grid；未套用原 4-step LoRA 或尺寸匹配 sigma。

這些個人執行紀錄、輸入圖、輸出圖與完整日誌未放入公開包。上述為目前安裝的功能驗證，未量測峰值記憶體，也不是正式的硬體速度比較。

## Apple M4 裝置證據

目前安裝於 2026-10-10 的原有工作流程日誌明確包含下列装置行。此處僅列出不含個人路徑與提示詞的片段：

```text
ggml_metal_device_init: GPU name:   MTL0 (Apple M4)
ggml_metal_init: found device: Apple M4
ggml_metal_init: picking default device: Apple M4
```

這可確認原有流程曾在 Apple M4 執行。2026-10-11 的 warm engine 工作日誌沒有各自列出硬體名稱，所以本包不將它們宣稱為獨立的 M4 效能測試，也不沿用上游 M5 的速度／記憶體數字。

## 不下載模型的回歸檢查

乾淨原始碼副本已放在含空格的資料夾啟動本機 UI，並確認網頁與 `/api/state` 能載入、4-step／8-step／圖片助手／放大器均辨識現有模型，佇列為空。此檢查未提交新圖片工作，也不包含重新下載大型模型。

新版安裝器另在隔離的暫存副本完成真實原生程式安裝：從固定 release 下載兩個 stable-diffusion.cpp 壓縮檔與 llama.cpp 壓縮檔，核對大小／SHA-256、解壓及安裝憑證；七個模型使用目前已核對的本機檔案，沒有重新下載大型權重。這證明本機的下載與安裝流程可執行，仍不等同於每個 macOS 環境都已測試。

發布前最新檢查：32 項 Python 與 4 項前端回歸檢查通過，shell 語法与文件相對連結檢查通過。GitHub Actions 工作流程已隨包提供，但尚未在使用者的新 GitHub 專案上執行。

在專案資料夾執行：

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/test_ui_turbo8.js
```

Python 檢查涵蓋推論參數、模型切換、安裝／啟動流程，以及命令列腳本的失敗回報與暫存清理；Node 檢查實際前端的模式保持、尺寸／參考細節切換、設定重用與送出參數。Node 只供維護測試使用，安裝與操作 UI 不需要 Node。

這些回歸檢查使用外部程序／下載的替代物，不執行 GPU 推論，不能用來證明出圖速度或記憶體占用。使用者仍應依 [M4 安裝教學](INSTALL-M4-16GB.md) 跑三項實際自測。
