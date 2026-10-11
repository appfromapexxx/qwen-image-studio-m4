# 模型與原生程式來源

本包在安裝時直接從發布者下載檔案，不包含權重或原生執行檔。以下為 2026-10-11 核對的組合；七個模型的 SHA-256 與目前本機安裝一致。下載程式固定 Hugging Face revision／GitHub release，並核對檔案大小及 SHA-256。

## 模型

| 本機檔名 | 用途 | 大小（十進位 GB） | 來源授權 |
|---|---|---:|---|
| [models/qwen-image-2.1-Q4_K_M.gguf](https://huggingface.co/unsloth/Qwen-Image-2.1-GGUF/resolve/2c31ccd392b367a6637841a143813320a02dff55/qwen-image-2.1-Q4_K_M.gguf) | 4-step 及一般模式基礎模型 | 4.200 | Qwen Research |
| [models/Qwen3-VL-8B-Instruct-UD-Q4_K_XL.gguf](https://huggingface.co/unsloth/Qwen3-VL-8B-Instruct-GGUF/resolve/b93a7ee713758252c555be4210c00540df954dc2/Qwen3-VL-8B-Instruct-UD-Q4_K_XL.gguf) | 共用文字／圖片理解模型 | 5.149 | Apache-2.0 |
| [models/mmproj-Qwen3VL-8B-Instruct-F16.gguf](https://huggingface.co/unsloth/Qwen3-VL-8B-Instruct-GGUF/resolve/b93a7ee713758252c555be4210c00540df954dc2/mmproj-F16.gguf) | 共用視覺投影模型 | 1.159 | Apache-2.0 |
| [models/qwen_image_2.1_vae_bf16.safetensors](https://huggingface.co/unsloth/Qwen-Image-2.1-FP8/resolve/bb21a8ba7f0371c19ad1f72c82a5e8fc10f39939/vae/qwen_image_2.1_vae_bf16.safetensors) | 共用 VAE | 0.676 | Qwen Research |
| [models/loras/fun-acc-4step.safetensors](https://huggingface.co/eastmoe/Qwen-Image-2.1-Fun-Acc-LoRAs-Comfy/resolve/b7bda1bebf7ccd6b9d15f48ed53f0012cd389099/Qwen-Image-2.1-Fun-Acc-4Step-comfyui.safetensors) | 4-step 加速 LoRA | 0.345 | Qwen Research |
| [models/Qwen-Image-2.1-Turbo-AD-Q4_K.gguf](https://huggingface.co/AtomicChat/Qwen-Image-2.1-Turbo-GGUF/resolve/bb25d06bc74119c12207243d68917951e6d9c232/Qwen-Image-2.1-Turbo-AD-Q4_K.gguf) | Turbo 8-step 生圖模型 | 4.202 | Qwen Research |
| [models/upscalers/RealESRGAN_x4plus.pth](https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth) | 2×／4× 放大模型 | 0.067 | BSD-3-Clause（來源倉庫） |

模型合計約 15.80 GB，另需原生程式、暫存與輸出空間。建議首次安裝預留至少 25 GB。檔案大小不是推論時的峰值 RAM。

## 校驗碼

下列雜湊核對已安裝檔案與公開 Hugging Face LFS metadata；Real-ESRGAN release 未提供 digest，其雜湊取自目前已安裝的檔案。

```text
631d532e7ca71e8d90a87c71d3699761a812039d22e3370e87498d87754660fe  models/qwen-image-2.1-Q4_K_M.gguf
e3d1a6e87c5cb31e054f2c3bc0dd82ffde052f613de5eef3665b7bd33c9b703e  models/Qwen3-VL-8B-Instruct-UD-Q4_K_XL.gguf
d406d03ebabefdef86a2c86bf0c1b65f9e046f7a81c218f25de4931b46a07fc4  models/mmproj-Qwen3VL-8B-Instruct-F16.gguf
71879ffd5321e6d10c3c87513e2b474b1252efa7f3dec2969214a9bf06a6dd5c  models/qwen_image_2.1_vae_bf16.safetensors
df86680547858d682bebfeb3a1523d4913f7fe837da34662af4b27a4a4c824a6  models/loras/fun-acc-4step.safetensors
4bb73c53cbe284bbd6d69b9fdc59539c531f0389dd2aa567663d777f8130bc59  models/Qwen-Image-2.1-Turbo-AD-Q4_K.gguf
4fa0d38905f75ac06eb49a7951b426670021be3018265fd191d2125df9d682f1  models/upscalers/RealESRGAN_x4plus.pth
```

## 原生程式

| 元件 | 固定版本 | 安裝位置 |
|---|---|---|
| [leejet/stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp/releases/download/master-929-3f8527a/sd-master-3f8527a-bin-Darwin-macOS-26.6.2-arm64.zip) | master-929-3f8527a | `bin/` |
| [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp/releases/download/b11249/llama-b11249-bin-macos-arm64.tar.gz) | b11249 | `bin/llama/` |
| [stable-diffusion.cpp：Turbo 8-step](https://github.com/leejet/stable-diffusion.cpp/releases/download/master-956-1b0ba10/sd-master-1b0ba10-bin-Darwin-macOS-26.6.2-arm64.zip) | master-956-1b0ba10 | `bin/turbo8/` |

兩個 stable-diffusion.cpp arm64 版本的 Mach-O minimum OS 均為 macOS 26.0。下載檔名中的 26.6.2 是發布者的建置標籤；本安裝路徑不承諾支援 macOS 15 或更舊版本。llama.cpp 的讀圖助手為另一個程序，並非同時載入第二套生圖模型。

原生壓縮檔 SHA-256（前兩項取自 GitHub release asset metadata，Turbo 8-step 亦已核對）：

```text
1c8ee6c8e413e3335b1223bbc657ea5d86dae1819f8426a98b84c265587eb192  sd-master-3f8527a-bin-Darwin-macOS-26.6.2-arm64.zip
d5fb90058f8d0c73c1e687b406dc1a6f53c64de725d3e642ae210db90c0b6613  llama-b11249-bin-macos-arm64.tar.gz
72c18ca1ba4177ca77cd288a9cb1e0f78d63ad3bde4b91fd7c84f3f4187b5761  sd-master-1b0ba10-bin-Darwin-macOS-26.6.2-arm64.zip
```

## 授權來源

- 程式：上游 [MIT LICENSE](https://github.com/sanketshinde3001/qwen-image-studio/blob/main/LICENSE)，完整保留於本包 [LICENSE](LICENSE)。
- Qwen-Image 基礎與 Turbo：官方 [2.1 LICENSE](https://huggingface.co/Qwen/Qwen-Image-2.1/blob/main/LICENSE)／[Turbo LICENSE](https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo/blob/main/LICENSE)。研究／評估用途；商業使用需依來源另取得授權。
- Fun-Acc：官方 [LICENSE](https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Acc-LoRAs/blob/main/LICENSE)／[NOTICE](https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Acc-LoRAs/blob/main/NOTICE)，轉換來源 [eastmoe](https://huggingface.co/eastmoe/Qwen-Image-2.1-Fun-Acc-LoRAs-Comfy)。
- Qwen3-VL：[官方模型與授權](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct/blob/main/LICENSE)，[Unsloth 量化來源](https://huggingface.co/unsloth/Qwen3-VL-8B-Instruct-GGUF)。
- 原生引擎：[stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp)、[llama.cpp](https://github.com/ggml-org/llama.cpp)，安裝壓縮檔保留其隨附授權。
- 放大器：[Real-ESRGAN LICENSE](https://github.com/xinntao/Real-ESRGAN/blob/master/LICENSE)。

本包不把下載模型改授權成 MIT。模型名稱用於描述相容性與來源；本包是社群控制介面，並非 Qwen 官方 UI。
