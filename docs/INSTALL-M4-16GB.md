# M4 Image Studio：M4 16GB 安裝與自測

M4 Image Studio 使用 Qwen-Image 2.1，本教學以 Apple Silicon M4、16GB 統一記憶體為目標，從下載 ZIP 到第一次產生與編輯圖片。原有工作流程已有明列 Apple M4 GPU 的本機紀錄；Turbo 8-step 已通過 512 文生圖、768 文生圖及 768 圖片編輯的功能驗證，但該批紀錄未列硬體，不能據此宣稱它在 M4 的速度或峰值記憶體。詳見 [驗證紀錄](VALIDATION.md)，並用下方流程測量自己的電腦。

## 1. 準備電腦

- 在「系統設定 → 一般 → 關於本機」確認晶片與記憶體；本安裝包需要 Apple Silicon。
- macOS 需為 **26.0 以上**。下載的 stable-diffusion.cpp arm64 引擎最低系統需求已確認為 26.0。
- 首次安裝建議預留 **25GB** 磁碟空間。模型合計約 **15.8GB**，還需要引擎、下載暫存與日後的圖片空間。
- 準備可連線至 GitHub 與 Hugging Face 的網路，供首次下載。

介面需要 **Python 3.9 以上**，使用 Python 標準函式庫，不需要 pip 或 CUDA。

## 2. 解壓 ZIP，開啟所在資料夾的終端機

1. 在你使用的 GitHub 專案頁面選 **Code → Download ZIP**。
2. 雙擊 ZIP 解壓縮，進入資料夾。
3. 確認能直接看見 `install.sh`、`studio.sh`、`README.md` 與 `studio/`。
4. 打開「終端機」，輸入 `cd `，注意最後有一個空格。
5. 把這個資料夾從 Finder 拖進終端機，再按 Return。資料夾路徑會自動填入，包含空格也能處理。

接下來的指令都在這個資料夾中執行。你可以輸入 `ls`，確認輸出中有 `install.sh`；若沒有，先進入正確的資料夾。

## 3. 先檢查環境

```bash
bash install.sh --check
```

這個指令只檢查安裝環境，不會下載模型。請依畫面結果處理缺少的項目，再執行一次。

如果缺少 Python，可選擇其中一種方式：

- **圖形安裝程式：** 從 [Python 官方 macOS 下載頁](https://www.python.org/downloads/macos/) 取得穩定版安裝程式，打開安裝；完成後重新開啟終端機。
- **已有 Homebrew：** 執行 `brew install python`，完成後重新開啟終端機。

可用以下指令查看終端機找到的 Python 版本：

```bash
python3 --version
```

版本需至少為 3.9。這個專案不需要額外執行 `pip install`。

## 4. 安裝模型與引擎

```bash
bash install.sh
```

也可以在 Finder 雙擊 **Install.command**。兩個入口會執行同一套安裝流程。

安裝順序為：

1. 原 Qwen-Image 2.1 GGUF、共用文字／視覺編碼器、VAE 與 Fun-Acc 4-step LoRA。
2. 原生推論引擎、圖片助手與圖片放大模型。
3. Turbo 8-step GGUF 與對應的推論引擎。

| 模型 | 約略下載大小，十進位 GB |
| --- | ---: |
| 原 Qwen-Image 2.1 Q4_K_M | 4.20 |
| Qwen3-VL 文字／視覺編碼器 | 5.15 |
| 視覺投影模型 | 1.16 |
| VAE | 0.68 |
| Fun-Acc 4-step LoRA | 0.34 |
| Real-ESRGAN 放大模型 | 0.07 |
| Turbo 8-step AD Q4_K | 4.20 |
| **合計** | **約 15.8** |

原生引擎另占少量空間。Finder 顯示的大小可能與表格略有差異；執行時的記憶體需求不能從檔案大小直接推算。

第一次下載請等待完成。若網路中斷，可在同一資料夾重新執行 `bash install.sh`；下載流程會保留已完成檔案，並嘗試續傳未完成的檔案。

**只補裝 Turbo 8-step：** 適用於已完成原本基礎安裝的人：

```bash
bash download.sh --turbo8
```

這個進階指令只補 Turbo 8-step 的模型與引擎，**不會下載共用文字編碼器、視覺投影或 VAE**。第一次安裝請使用 `bash install.sh`；若手動安裝，先執行 `bash download.sh`，完成後再執行 `bash download.sh --turbo8`。

## 5. 啟動瀏覽器介面

```bash
bash studio.sh
```

也可以雙擊 **Start.command**。瀏覽器應開啟 [http://127.0.0.1:7860](http://127.0.0.1:7860)。若沒有自動開啟，可自行點這個連結。

保留終端機視窗讓程式持續執行。要停止時，在終端機按 **Control + C**。

如果 7860 已被其他程式使用，可換一個連接埠：

```bash
bash studio.sh 8080
```

此時使用 [http://127.0.0.1:8080](http://127.0.0.1:8080)。網址中的 `127.0.0.1` 代表你的電腦；不是對外發布的網站。

## 6. 了解介面設定

- **Generate：** 用文字產生圖片，可輸入中文或英文。
- **Edit：** 上傳圖片並描述修改指令；最多加入 3 張參考圖。
- **⚡ Turbo：** 保留原本的 4-step LoRA 路線，也是啟動時的預設。
- **Turbo 8-step：** 使用官方 Turbo checkpoint 的 AtomicChat 社群 GGUF 量化版。固定 8 steps、CFG 1、Euler 與官方 9 點 sigma 排程。
- **Size：** 512 適合先確認安裝與流程；通過後再試 768。改尺寸仍保留 Turbo 8-step 模式。
- **Reference detail：** 預設 1024，控制參考圖讀取細節。它不代表輸出一定是 1024。
- **Seed：** `-1` 代表每次隨機。自測時填入固定數字，例如 `42`，並開啟旁邊的鎖定按鈕，讓後續工作繼續用同一個種子。
- **Queue / Gallery：** 工作按順序處理；完成後會出現在圖庫，可重用設定、下載或繼續編輯。

Turbo 8-step 的灰色設定已鎖定或被跳過，包括負面提示詞、Image guidance、Fast mode 與 Flow shift。舊 4-step 的 LoRA 與尺寸匹配排程選項不適用於這個模式。

## 用相同提示詞與種子自測

測試前先關閉不需要的高記憶體程式。先跑一張圖片，再增加尺寸；不要同時開兩個 Studio 執行推論。

### A. 512 × 512 文生圖

1. 選 **Generate → Turbo 8-step → 512 → 1:1**。
2. 展開 **More settings**，將 **Seed** 設為 `42`，開啟種子鎖定；**Variations** 保持 `1`。
3. 使用下方固定提示詞，按 **Generate**。

   ```text
   A red ceramic mug on a wooden table, soft natural window light, a simple background, photorealistic product photography.
   ```

4. 等待工作完成，確認圖庫中有 512 × 512 圖片。打開圖片詳情，檢查 8 steps、CFG 1、Euler 和 Turbo 8-step 標示。

### B. 768 × 768 文生圖

保留同一段提示詞與 Seed `42`，只把 Size 改為 **768**，再次產生。確認選中的仍然是 **Turbo 8-step**，並檢查輸出為 768 × 768。

若要與舊 **⚡ Turbo** 比較，使用相同尺寸、提示詞與 Seed `42` 各產生一張，記錄兩個模式。相同種子可讓設定比較更一致，但兩種模型或不同尺寸不保證產生相同構圖。

### C. 768 × 768 圖片編輯

1. 在 B 的輸出圖上選 **Edit**，或在 Edit 頁籤上傳這張 768 × 768 圖片。
2. 選 **Turbo 8-step → 768**，保持 **Match** 長寬比、Reference detail **1024** 與 Seed **42**。
3. 使用以下指令，按 **Edit**：

   ```text
   Change the mug to blue. Keep the shape of the mug, the wooden table, and the original lighting.
   ```

4. 確認編輯完成、輸出尺寸正確，杯子顏色改變且主要場景保留。可用圖片詳情的前後對照查看。

中文也可以使用。想比較中文與英文時，請各自重用同一張原圖，保持尺寸與 Seed 一致：

```text
把馬克杯改成藍色，保留杯子的形狀、木桌和原本的光線。
```

若只想改一小塊，點參考圖上的 **Mask**，塗出杯子範圍，再使用相同指令。第一次自測先不加遮罩，以便確認基本編輯流程。

### 記錄你的結果

| 項目 | 請自己填寫 |
| --- | --- |
| 晶片／統一記憶體／macOS | 例如 M4、16GB、實際系統版本 |
| 使用的模式／提示詞／種子 | 記錄 Turbo 8-step 或 ⚡ Turbo、完整提示詞、Seed |
| 三項測試 | 512 文生圖、768 文生圖、768 編輯是否完成 |
| 耗時 | 第一次與第二次分開記錄；第一次包含引擎與模型載入 |
| 記憶體狀況 | 可在「活動監視器 → 記憶體」觀察記憶體壓力與交換空間 |

這份教學不提供 M4 實測秒數或 Turbo 8-step RAM 保證。介面的預估時間是本機使用紀錄形成的估算。

## 圖片與設定存在哪裡

一般模式下，檔案保存在你解壓縮的專案資料夾：

| 資料夾 | 內容 |
| --- | --- |
| `outputs/` | 產生或編輯的圖片，以及同名 `.json` 設定 |
| `inputs/` | 上傳的參考圖與遮罩 |
| `logs/` | 工作記錄，供排查錯誤 |
| `models/` | 下載的模型 |
| `bin/` | 下載的本機引擎 |

私密模式的結果需要另行下載或按 **Keep** 才會保留為一般圖庫檔案。分享問題時可貼錯誤訊息；公開原始碼時請使用乾淨包，保留自己的圖片在本機。

## 常見問題

**`install.sh` 找不到。** 目前終端機位置不在專案資料夾。重新用上面的 `cd `＋拖入資料夾方式，確認 `ls` 看得到 `install.sh`。

**雙擊 command 檔無法開啟。** 在資料夾的終端機中使用 `bash install.sh` 或 `bash studio.sh`。ZIP 經網頁下載或上傳後可能無法保留可執行權限，這兩個指令不需要替腳本另外設定權限。

**環境檢查顯示系統或架構不符。** 本包的預編譯引擎需要 Apple Silicon 與 macOS 26.0 以上。請先處理環境需求，再下載模型。

**Turbo 8-step 按鈕是灰色。** 模型或該模式引擎可能尚未下載完成。在正確資料夾重新執行 `bash install.sh`，完成後重新啟動 Studio；已有基礎安裝可使用 `bash download.sh --turbo8`。

**下載中斷或驗證失敗。** 先確認網路與磁碟空間，再重新執行安裝器。若同一個檔案仍持續失敗，保留完整錯誤訊息，依安裝器顯示的檔名排查。

**之前已安裝，為何又下載引擎？** 新版會用本機安裝憑證驗證引擎檔案；舊安裝沒有憑證時，第一次重跑可能補抓小型引擎壓縮檔，已完成且驗證通過的模型不會重新下載。

**瀏覽器無法連線。** 確認啟動的終端機視窗仍在執行，網址中的連接埠與啟動指令一致。若已按 Control + C，需重新啟動。

**工作變慢或記憶體壓力很高。** 先使用 512、單張變化，等佇列完成後再執行下一張；關閉大型程式。首次載入與連續運行的熱度都可能影響時間，不能用一次結果推定所有 M4 的速度。

## 來源與授權

應用程式保留上游 Sanket Shinde 的 [MIT 授權](../LICENSE) 與 [來源標示](../NOTICE.md)。Qwen-Image 2.1 與 Turbo 模型的 [官方研究授權](https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo/blob/main/LICENSE) 限研究／評估用途，商用需另取得授權。模型與引擎另受各自授權約束，詳見 [MODEL_SOURCES.md](../MODEL_SOURCES.md)。官方 Turbo checkpoint 與本包下載的社群 GGUF 是不同發布物，請閱讀相應來源的授權。

## 致謝

感謝 [Qwen 官方團隊](https://github.com/QwenLM/Qwen-Image-2.1) 提供 Qwen-Image 2.1 與 Turbo 模型。

感謝原 UI 作者 [Sanket Rajendra Shinde](https://github.com/sanketshinde3001/qwen-image-studio) 開發 Qwen-Image Studio。本包在他的 UI 上整理 Mac 安裝方式，新增 Turbo 8-step 路線與這份繁體中文教學，並完整保留上游 MIT 授權與作者標示。
