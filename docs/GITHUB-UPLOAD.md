# 把乾淨原始碼包上傳到自己的 GitHub

這份教學由你建立自己的 GitHub 專案，再上傳 **M4 Image Studio — 使用 Qwen-Image 2.1** 的乾淨原始碼。安裝器與模型下載腳本會一起保留；大型模型及自己的圖片留在本機。本包沒有替你建立或發布 GitHub 專案。

## 先認識正確的資料夾位置

打開原始碼包的資料夾，應直接看到：

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

上傳時選取這些**檔案與子資料夾內容**，讓 `README.md` 和 `install.sh` 位於 GitHub 專案的最外層。`studio/`、`docs/`、`tests/` 和 `.github/` 要維持原本的子資料夾。`.github/` 包含自動檢查流程；`.gitattributes` 保留腳本使用的 LF 換行設定。

例如，本機有 `qwen-image-studio-m4/README.md`，上傳後應看到專案根目錄的 `README.md`。不要再多包一層 `qwen-image-studio-m4/`，也不要把 ZIP 檔本身當成全部原始碼上傳。

如果你已經在這個資料夾安裝或使用過，請另取一份**尚未安裝的乾淨原始碼包**來上傳。乾淨包不包含 `models/`、`bin/`、`inputs/`、`outputs/`、`logs/`、個人截圖或本機設定。

## 方法一：用 GitHub 網頁上傳

### 1. 建立空白專案

1. 登入自己的 GitHub 帳號，開啟 [建立新專案](https://github.com/new)。
2. **Owner** 選自己的帳號，填入專案名稱；例如 `m4-image-studio`，名稱由你決定。
3. 依分享需求選 **Public** 或 **Private**。
4. 保持 README、`.gitignore` 和 License 的自動新增選項關閉，因為乾淨包已經包含這些檔案。
5. 按 **Create repository**。

這個流程是 GitHub 的 [建立專案方式](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)；建立空專案可避免與包內檔案重複。

### 2. 上傳包內內容

1. 空專案頁面上點 **uploading an existing file**；若已經有檔案，使用 **Add file → Upload files**。
2. 在 Finder 打開乾淨包資料夾，按 **Command + Shift + .** 顯示隱藏檔案。
3. 選取包內檔案與 `studio/`、`docs/`、`tests/`、`.github/` 子資料夾，拖進上傳區域。確認 `.gitignore` 和 `.gitattributes` 也有加入。
4. 檢查待上傳的檔名：應包含 `studio/server.py`、`studio/engine.py`、`studio/index.html`、`docs/INSTALL-M4-16GB.md` 與 `.github/workflows/checks.yml`。
5. 確認沒有多出外層 `qwen-image-studio-m4/`，也沒有模型或個人圖片。
6. 填入提交說明，例如 `加入 Mac 安裝包與繁體中文教學`，按 **Commit changes** 完成第一筆提交。

GitHub 支援拖放檔案或資料夾；瀏覽器每個檔案上限為 25 MiB，每次最多 100 個檔案。這份乾淨包只放小型原始碼，模型由安裝器另行下載。詳見 [GitHub 官方上傳說明](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)。

**網頁上傳不會讀取 `.gitignore` 來替你過濾檔案。** 即使已上傳 `.gitignore`，仍須自己確認沒有把模型或個人圖片拖進上傳區域。

### 3. 檢查隱藏檔案與目錄

回到專案首頁，確認 `.gitignore`、`.gitattributes` 和 `.github/` 都出現在檔案清單中，並可打開 `.github/workflows/checks.yml`。`.gitignore` 會讓日後用 Git 管理專案時略過模型、引擎、圖片與本機狀態。

若瀏覽器漏掉隱藏檔案，可逐一補上：

1. 在 Finder 用 **Command + Shift + .** 顯示隱藏檔案，用文字編輯器打開缺少的那一份。
2. 在 GitHub 選 **Add file → Create new file**。
3. 檔名填入完整路徑，例如 `.gitignore`、`.gitattributes` 或 `.github/workflows/checks.yml`，複製乾淨包中該檔案的完整內容。
4. 提交後再次核對這三個檔案；網頁上傳不會依 `.gitattributes` 自動轉換換行，請原樣保留包內檔案內容。

### 4. 用自己的 ZIP 測試一次

1. 在剛建立的專案按 **Code → Download ZIP**。
2. 解壓到一個新資料夾，確認最外層直接有 `install.sh` 和 `studio/`。
3. 在這個新資料夾的終端機執行：

   ```bash
   bash install.sh --check
   ```

4. 環境通過後，可照 [安裝教學](INSTALL-M4-16GB.md) 執行 `bash install.sh` 與 `bash studio.sh`。

用 `bash` 啟動可避開網頁上傳未保留腳本可執行權限的問題。雙擊入口仍有提供；若雙擊無法開啟，就使用終端機指令。

## 方法二：已熟悉 Git 的使用者

請在**乾淨原始碼包資料夾**開啟終端機，並先照方法一建立不含預設檔案的空白 GitHub 專案。

```bash
git init -b main
git add .
git status --short
```

檢查待提交清單，應只有原始碼、文件、啟動腳本、授權與 `.gitignore`。若出現自己的圖片、模型或其他無關資料，先處理檔案範圍，再繼續。

```bash
git commit -m "加入 Mac 安裝包與繁體中文教學"
```

接著，從你剛建立的 GitHub 專案頁面複製 **HTTPS** 網址，替換下一段中整個示例網址。`YOUR_USERNAME` 與 `YOUR_REPOSITORY` 是佔位字，不是已存在的專案：

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

若 Git 提示需要設定作者名稱或登入，依自己的帳號資訊完成即可；本教學不會代替你建立帳號、設定身份或推送檔案。若不熟悉 Git，使用網頁上傳方法即可。

## 發布後確認

- 專案首頁直接顯示繁體中文 README。
- 根目錄有 `install.sh`、`studio.sh`、`Install.command`、`Start.command`、`.gitignore` 與 `.gitattributes`。
- `.github/workflows/checks.yml` 保留在原本路徑，供 GitHub 執行自動檢查。
- `studio/` 保留三個程式檔；`docs/` 的安裝與上傳連結可開啟。
- `LICENSE`、`NOTICE.md` 與 `MODEL_SOURCES.md` 保留在根目錄。
- 下載的新 ZIP 中可以執行 `bash install.sh --check`。
- GitHub 檔案清單沒有模型、引擎、個人上傳圖、輸出、截圖或工作記錄。

應用程式保留 Sanket Shinde 的 MIT 授權與上游來源標示。模型及引擎適用各自授權，請保留 [來源文件](../MODEL_SOURCES.md) 與 [NOTICE.md](../NOTICE.md)，不要用自己建立的專案名稱取代上游作者的授權文字。

也請保留 [README 的致謝](../README.md#致謝) 與 [安裝教學的致謝](INSTALL-M4-16GB.md#致謝)，讓使用者知道模型來自 Qwen 官方，原 UI 由 Sanket Rajendra Shinde 開發。
