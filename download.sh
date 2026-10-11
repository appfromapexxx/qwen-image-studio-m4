#!/bin/bash
# Original setup by default; --turbo8 adds the official 8-step model and a separate engine.
set -euo pipefail
cd "$(dirname "$0")"
source ./install.sh
case "${1:-}" in
  ""|--turbo8) ;;
  *) echo "Usage: bash download.sh [--turbo8]" >&2; exit 2 ;;
esac
[ "$#" -le 1 ] || { echo "Usage: bash download.sh [--turbo8]" >&2; exit 2; }
check_environment
mkdir -p bin/llama models/loras models/upscalers outputs inputs logs

HF=https://huggingface.co
SD_URL=https://github.com/leejet/stable-diffusion.cpp/releases/download/master-929-3f8527a/sd-master-3f8527a-bin-Darwin-macOS-26.6.2-arm64.zip
LLAMA_URL=https://github.com/ggml-org/llama.cpp/releases/download/b11249/llama-b11249-bin-macos-arm64.tar.gz
TURBO8_SD_URL=https://github.com/leejet/stable-diffusion.cpp/releases/download/master-956-1b0ba10/sd-master-1b0ba10-bin-Darwin-macOS-26.6.2-arm64.zip
LLAMA_SHA=d5fb90058f8d0c73c1e687b406dc1a6f53c64de725d3e642ae210db90c0b6613
LLAMA_FILES=(llama-mtmd-cli libllama.dylib libmtmd.dylib libllama-common.dylib libggml.dylib libggml-base.dylib libggml-cpu.dylib libggml-metal.dylib libggml-blas.dylib libggml-rpc.dylib
             libllama.0.dylib libmtmd.0.dylib libllama-common.0.dylib libggml.0.dylib libggml-base.0.dylib libggml-cpu.0.dylib libggml-metal.0.dylib libggml-blas.0.dylib libggml-rpc.0.dylib)
DOWNLOAD_STAGE=""
trap 'if [ -n "$DOWNLOAD_STAGE" ]; then rm -rf "$DOWNLOAD_STAGE"; fi' EXIT

verify_hash() {
  printf '%s  %s\n' "$2" "$1" | shasum -a 256 -c - >/dev/null
}

fetch() {  # fetch <dest> <pinned URL> <expected bytes> <SHA256>
  local dest="$1" url="$2" expected="$3" checksum="$4" size=0
  if [ -f "$dest" ]; then
    size=$(stat -f%z "$dest") || return 1
    if [ "$size" -eq "$expected" ]; then
      if verify_hash "$dest" "$checksum"; then
        echo "ok        $dest"
        return 0
      fi
      echo "Replacing a file that failed SHA256 verification: $dest" >&2
      rm -f "$dest" || return 1
    elif [ "$size" -gt "$expected" ]; then
      echo "Replacing an oversized file: $dest" >&2
      rm -f "$dest" || return 1
    fi
  fi
  echo "download  $dest"
  curl --location --fail --retry 3 -C - -o "$dest" "$url" || return $?
  size=$(stat -f%z "$dest") || return 1
  if [ "$size" -ne "$expected" ]; then
    echo "Download size mismatch for $dest: expected $expected bytes, got $size. Run again to resume." >&2
    return 1
  fi
  if ! verify_hash "$dest" "$checksum"; then
    echo "Download failed SHA256 verification: $dest. Run again to download a fresh copy." >&2
    rm -f "$dest"
    return 1
  fi
}

bundle_receipt_ok() {
  [ -f "$1/.studio-source.sha256" ] && [ -s "$1/.studio-files.sha256" ] || return 1
  [ "$(cat "$1/.studio-source.sha256")" = "$2" ] || return 1
  (cd "$1" && shasum -a 256 -c .studio-files.sha256 >/dev/null 2>&1)
}

write_bundle_receipt() {
  local dir="$1" checksum="$2"
  shift 2
  (cd "$dir" && shasum -a 256 "$@" > .studio-files.sha256 && printf '%s\n' "$checksum" > .studio-source.sha256)
}

sd_payload_ok() {
  [ -s "$1/sd-cli" ] && [ -s "$1/sd-server" ] && [ -s "$1/libstable-diffusion.dylib" ] || return 1
}

sd_bundle_ok() {
  sd_payload_ok "$1" && bundle_receipt_ok "$1" "$2" || return 1
  chmod +x "$1/sd-cli" "$1/sd-server"
}

ensure_sd_bundle() {
  local dir="$1" archive="$2" url="$3" size="$4" checksum="$5"
  if sd_bundle_ok "$dir" "$checksum"; then return 0; fi
  fetch "$archive" "$url" "$size" "$checksum" || return $?
  DOWNLOAD_STAGE=$(mktemp -d "$PWD/bin/.unpack.XXXXXX") || return 1
  unzip -oq "$archive" -d "$DOWNLOAD_STAGE" || return $?
  if ! sd_payload_ok "$DOWNLOAD_STAGE"; then
    echo "Native engine bundle is incomplete: $dir (sd-cli, sd-server and shared library are required)." >&2
    return 1
  fi
  write_bundle_receipt "$DOWNLOAD_STAGE" "$checksum" sd-cli sd-server libstable-diffusion.dylib || return 1
  mkdir -p "$dir" || return 1
  cp -Rp "$DOWNLOAD_STAGE/." "$dir/" || return 1
  if ! sd_bundle_ok "$dir" "$checksum"; then
    echo "Native engine validation failed: $dir. Run the installer again to repair it." >&2
    return 1
  fi
  rm -rf "$DOWNLOAD_STAGE"
  DOWNLOAD_STAGE=""
  rm -f "$archive"
}

llama_payload_ok() {
  local file
  for file in "${LLAMA_FILES[@]}"; do
    [ -s "$1/$file" ] || return 1
  done
}

llama_bundle_ok() {
  local dir=bin/llama/llama-b11249
  llama_payload_ok "$dir" && bundle_receipt_ok "$dir" "$LLAMA_SHA" || return 1
  chmod +x "$dir/llama-mtmd-cli"
}

if [ "${1:-}" = "--turbo8" ]; then
  fetch models/Qwen-Image-2.1-Turbo-AD-Q4_K.gguf "$HF/AtomicChat/Qwen-Image-2.1-Turbo-GGUF/resolve/bb25d06bc74119c12207243d68917951e6d9c232/Qwen-Image-2.1-Turbo-AD-Q4_K.gguf" 4201694944 4bb73c53cbe284bbd6d69b9fdc59539c531f0389dd2aa567663d777f8130bc59
  ensure_sd_bundle bin/turbo8 bin/turbo8.zip "$TURBO8_SD_URL" 35158090 72c18ca1ba4177ca77cd288a9cb1e0f78d63ad3bde4b91fd7c84f3f4187b5761
  echo "Turbo 8-step ready. Double-click Start.command to open M4 Image Studio."
  exit 0
fi

ensure_sd_bundle bin bin/sd.zip "$SD_URL" 35049086 1c8ee6c8e413e3335b1223bbc657ea5d86dae1819f8426a98b84c265587eb192
if ! llama_bundle_ok; then
  fetch bin/llama.tar.gz "$LLAMA_URL" 11763877 "$LLAMA_SHA"
  DOWNLOAD_STAGE=$(mktemp -d "$PWD/bin/.unpack.XXXXXX")
  tar -xzf bin/llama.tar.gz -C "$DOWNLOAD_STAGE"
  llama_payload_ok "$DOWNLOAD_STAGE/llama-b11249" || { echo "Qwen3-VL assistant archive is incomplete." >&2; exit 1; }
  write_bundle_receipt "$DOWNLOAD_STAGE/llama-b11249" "$LLAMA_SHA" "${LLAMA_FILES[@]}"
  cp -Rp "$DOWNLOAD_STAGE/." bin/llama/
  llama_bundle_ok || { echo "Qwen3-VL assistant bundle is incomplete; run the installer again." >&2; exit 1; }
  rm -rf "$DOWNLOAD_STAGE"
  DOWNLOAD_STAGE=""
  rm -f bin/llama.tar.gz
fi

fetch models/qwen-image-2.1-Q4_K_M.gguf "$HF/unsloth/Qwen-Image-2.1-GGUF/resolve/2c31ccd392b367a6637841a143813320a02dff55/qwen-image-2.1-Q4_K_M.gguf" 4199565024 631d532e7ca71e8d90a87c71d3699761a812039d22e3370e87498d87754660fe
fetch models/Qwen3-VL-8B-Instruct-UD-Q4_K_XL.gguf "$HF/unsloth/Qwen3-VL-8B-Instruct-GGUF/resolve/b93a7ee713758252c555be4210c00540df954dc2/Qwen3-VL-8B-Instruct-UD-Q4_K_XL.gguf" 5148699488 e3d1a6e87c5cb31e054f2c3bc0dd82ffde052f613de5eef3665b7bd33c9b703e
fetch models/mmproj-Qwen3VL-8B-Instruct-F16.gguf "$HF/unsloth/Qwen3-VL-8B-Instruct-GGUF/resolve/b93a7ee713758252c555be4210c00540df954dc2/mmproj-F16.gguf" 1159030336 d406d03ebabefdef86a2c86bf0c1b65f9e046f7a81c218f25de4931b46a07fc4
fetch models/qwen_image_2.1_vae_bf16.safetensors "$HF/unsloth/Qwen-Image-2.1-FP8/resolve/bb21a8ba7f0371c19ad1f72c82a5e8fc10f39939/vae/qwen_image_2.1_vae_bf16.safetensors" 675508656 71879ffd5321e6d10c3c87513e2b474b1252efa7f3dec2969214a9bf06a6dd5c
fetch models/loras/fun-acc-4step.safetensors "$HF/eastmoe/Qwen-Image-2.1-Fun-Acc-LoRAs-Comfy/resolve/b7bda1bebf7ccd6b9d15f48ed53f0012cd389099/Qwen-Image-2.1-Fun-Acc-4Step-comfyui.safetensors" 344600164 df86680547858d682bebfeb3a1523d4913f7fe837da34662af4b27a4a4c824a6
fetch models/upscalers/RealESRGAN_x4plus.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth 67040989 4fa0d38905f75ac06eb49a7951b426670021be3018265fd191d2125df9d682f1

echo "All files ready. Double-click Start.command to open M4 Image Studio."
