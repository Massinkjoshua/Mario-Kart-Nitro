#!/usr/bin/env bash
# Windows/MSYS2 build. Writes only this project's build/log folders.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
case "$(uname -s)" in
    MSYS*|MINGW*) ;;
    *) echo "Use build_linux.sh on Linux, or this wrapper on Windows/MSYS2."; exit 1 ;;
esac
case "$PWD" in
    *[[:space:]]*) echo "Extract into a path without spaces, such as C:/MKNitro_Source."; exit 1 ;;
esac
for command_name in make python3 tee; do
    command -v "$command_name" >/dev/null || { echo "Missing $command_name"; exit 1; }
done
for tool_file in tools/codewarrior/mwcceppc.exe tools/codewarrior/mwasmeppc.exe tools/kamek/Kamek.exe; do
    [[ -f "$tool_file" ]] || { echo "Missing supplied tool: $tool_file"; exit 1; }
done
mkdir -p logs
build_log=$(mktemp logs/build-XXXXXXXX.log)
exec > >(tee "$build_log") 2>&1
echo "Mario Kart Nitro source candidate; multi-config profile; log: $build_log"
if [[ -e build ]]; then
    mkdir -p build-history
    previous_build=$(mktemp -d build-history/run-XXXXXXXX)
    mv -- build "$previous_build/build"
fi
make -j2 all loader MKNITRO_SINGLE_CONFIG=0 CFLAGS= \
    CC=./tools/codewarrior/mwcceppc.exe AS=./tools/codewarrior/mwasmeppc.exe \
    KAMEK=./tools/kamek/Kamek.exe PYTHON=python3 SECURE=./external/not-bundled
python3 scripts/check_build_output.py
echo "Built build/Code.pul and build/Loader.pul. CurrentPack remains unchanged."
echo "See SOURCE_STATUS.md for the remaining latest-release implementation gaps."
