# M4 Image Studio — 使用 Qwen-Image 2.1

在 Mac 的瀏覽器中使用 Qwen-Image 2.1，輸入中文或英文產生圖片，也能上傳圖片並描述要修改的地方。模型與輸出保存在自己的電腦，介面預設使用原本的 **⚡ Turbo（4-step）**，另提供 **Turbo 8-step** 選項。

這份原始碼包為 **Apple Silicon M4、16GB 統一記憶體** 的使用者整理安裝流程。原有工作流程已有標示 **Apple M4 GPU** 的本機執行紀錄；Turbo 8-step 的功能驗證紀錄沒有硬體欄位，因此不宣稱它在 M4 的速度或峰值記憶體。建議先從 512 圖片開始，再自行測試 768。

Qwen-Image 2.1 與 Turbo 模型採 **Qwen Research License**，限研究／評估用途；商用需另取得授權。請先閱讀 [官方模型 LICENSE](https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo/blob/main/LICENSE)。應用程式本身保留上游 MIT 授權。

## 安裝前確認

| 項目 | 需求 |
| --- | --- |
| Mac | Apple Silicon；本教學以 M4、16GB 為目標 |
| 系統 | macOS **26.0 以上**；隨附下載流程使用的 arm64 引擎最低需求為 26.0 |
| Python | Python **3.9 以上**；介面使用標準函式庫 |
| 磁碟空間 | 首次安裝建議預留 **25GB**；完整模型約 **15.8GB**，另有引擎、暫存及產生的圖片 |
| 網路 | 首次下載模型與引擎需要網路；圖片推論在本機執行 |

不需要安裝 pip 套件或 CUDA。若缺少 Python，可使用 [Python 官方 macOS 安裝程式](https://www.python.org/downloads/macos/)，或在已有 Homebrew 的電腦執行 `brew install python`。

## 下載 ZIP 後怎麼用

1. 在這個 GitHub 專案頁面按 **Code → Download ZIP**，解壓縮並打開資料夾。
2. 確認目前資料夾中能看到 `install.sh`、`studio.sh` 和 `studio/`。
3. 在這個資料夾開啟「終端機」，先檢查環境：

   ```bash
   bash install.sh --check
   ```

4. 檢查通過後安裝：

   ```bash
   bash install.sh
   ```

   安裝器會先下載原本 4-step 路線、共用模型、圖片助手與放大模型，再下載 Turbo 8-step 模型及其引擎。第一次會下載約 15.8GB 模型，請等待完成。

5. 啟動：

   ```bash
   bash studio.sh
   ```

   瀏覽器會開啟 [本機介面](http://127.0.0.1:7860)。使用期間保留終端機視窗，結束時按 **Control + C**。

也可以雙擊 **Install.command** 安裝、雙擊 **Start.command** 啟動。若雙擊無法開啟，使用上面的 `bash` 指令即可。完整步驟與常見問題見 [M4 16GB 安裝教學](docs/INSTALL-M4-16GB.md)。

## 先產生一張，再試編輯

**產生圖片：** 選擇 **Generate**，預設的 **⚡ Turbo** 可直接使用。要試新模型，改選 **Turbo 8-step**，再選 **512** 或 **768**，輸入提示詞後按 **Generate**。

```text
一個紅色陶瓷馬克杯放在木桌上，柔和的窗邊自然光，背景簡潔，寫實產品攝影。
```

**編輯圖片：** 選擇 **Edit**，上傳或拖入圖片，輸入修改指令後按 **Edit**。例如：

```text
把馬克杯改成藍色，保留杯子的形狀、木桌和原本的光線。
```

上傳最多 **3 張參考圖**。**Reference detail** 預設為 **1024**，代表讀取參考圖的細節；輸出尺寸仍由 **Size** 決定。使用 **Mask** 可塗出想修改的範圍。

工作會依序進入佇列（Queue），完成後出現在圖庫（Gallery）。圖庫可重用設定、繼續編輯或下載圖片。一般輸出保存在本機 `outputs/`，同名 `.json` 記錄該張圖片的設定。不要把自己的圖片或參考圖一起上傳到 GitHub。

## 兩種 Turbo 有什麼差別

| 選項 | 使用的路線 | 步數與設定 |
| --- | --- | --- |
| **⚡ Turbo**，預設 | 原 Qwen-Image 2.1 的社群 GGUF，搭配 Fun-Acc 4-step LoRA 轉換檔 | 4 steps、CFG 1；保留原本依尺寸調整／原始排程選項 |
| **Turbo 8-step** | 官方 Qwen-Image 2.1 Turbo checkpoint 的 **AtomicChat 社群 GGUF 量化版**：`Qwen-Image-2.1-Turbo-AD-Q4_K.gguf` | 固定 8 steps、CFG 1、Euler、官方 9 點 sigma 排程；不套用 4-step LoRA |
| **Draft / Balanced / Quality** | 原 Qwen-Image 2.1 完整模型路線 | 保留原本的預設與可調參數 |

「官方 Turbo checkpoint」指上游模型；這裡下載的 GGUF 由社群量化與發布，**不是官方直接發布的 GGUF**。兩條路線共用文字／視覺編碼器及 VAE，安裝時不用再下載一份相同模型。

Turbo 8-step 的固定 sigma 排程為：

```text
1.0, 0.978453, 0.95418, 0.926626, 0.89508, 0.845148, 0.704534, 0.414568, 0.0
```

Turbo 8-step 會鎖定或跳過步數、CFG、負面提示詞、Image guidance、Fast mode、Sampler、Scheduler 和 Flow shift 等設定；改輸出尺寸不會改掉這條固定排程。

## 已確認的功能與實測範圍

先前的 Web UI 功能驗證已成功完成以下三項：

- Turbo 8-step：512 × 512 文生圖。
- Turbo 8-step：768 × 768 文生圖。
- Turbo 8-step：768 × 768 圖片編輯。

原有本機工作流程的紀錄已明列 Apple M4 GPU；上述 Turbo 8-step 測試的紀錄未列出硬體，因此不提供 Turbo 8-step 的 M4 秒數或 RAM 實測數字。驗證範圍與整理後的硬體摘錄見 [驗證紀錄](docs/VALIDATION.md)。介面的預估時間會隨本機執行紀錄調整，不能當成硬體保證。請依 [自測步驟](docs/INSTALL-M4-16GB.md#用相同提示詞與種子自測) 記錄自己的結果。

安裝組合的七個模型已比對本機檔案與固定來源版本的 SHA-256，來源資料便於重現這組模型；詳見下方模型來源文件。

## 這份原始碼包包含什麼

```text
README.md
LICENSE
NOTICE.md
MODEL_SOURCES.md
.gitignore
.gitattributes
.github/
install.sh
Install.command
Start.command
studio.sh
download.sh
generate.sh
edit.sh
studio/
docs/
tests/
```

原始碼包不包含模型、下載的引擎、個人圖片、輸出或截圖。安裝時會在本機建立 `models/`、`bin/`、`inputs/`、`outputs/` 和 `logs/` 等目錄。

`generate.sh` 與 `edit.sh` 保留原本命令列工作流程；本教學的 Turbo 8-step 操作以 Web UI 為主。若要把乾淨原始碼包上傳到自己的帳號，請照 [GitHub 上傳教學](docs/GITHUB-UPLOAD.md)。本包沒有替你建立或發布 GitHub 專案。

## 來源與授權

應用程式延續 [Sanket Shinde 的 Qwen-Image Studio](https://github.com/sanketshinde3001/qwen-image-studio)，保留上游 [MIT 授權](LICENSE) 與作者標示；本包新增 Mac 安裝入口、Turbo 8-step 路線與繁體中文文件。詳見 [NOTICE.md](NOTICE.md)。

Qwen-Image 2.1 與 Turbo 的 [官方研究授權](https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo/blob/main/LICENSE) 限研究／評估用途，商用需另取得授權。其他編碼器、LoRA、放大模型與原生引擎適用各自來源的授權，並不因應用程式採 MIT 而全部變成 MIT。下載來源與版本資訊見 [MODEL_SOURCES.md](MODEL_SOURCES.md)。

## 致謝

感謝 [Qwen 官方團隊](https://github.com/QwenLM/Qwen-Image-2.1) 提供 Qwen-Image 2.1 與 Turbo 模型，讓這套本機圖片工作流程得以實現。

感謝原 UI 作者 [Sanket Rajendra Shinde](https://github.com/sanketshinde3001/qwen-image-studio) 開發 Qwen-Image Studio。本包在他的 UI 基礎上整理 Mac 安裝流程，新增 Turbo 8-step 路線與繁體中文教學，並完整保留上游 MIT 授權與作者標示。
