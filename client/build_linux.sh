#!/usr/bin/env bash
# Linux x86_64 source candidate build, Mario Kart Nitro, 16 October 2026.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
case "$PWD" in
    *[[:space:]]*) echo "Extract into a path without spaces for the supplied compiler."; exit 1 ;;
esac
nitro_wibo=${NITRO_WIBO:-$PWD/tools/linux/wibo}
nitro_kamek=${NITRO_KAMEK:-$PWD/tools/linux/Kamek}
for command_name in make python3 tee; do
    command -v "$command_name" >/dev/null || { echo "Missing $command_name"; exit 1; }
done
if [[ ! -x "$nitro_wibo" || ! -x "$nitro_kamek" ]]; then
    echo "Run python3 scripts/fetch_linux_tools.py, or set NITRO_WIBO and NITRO_KAMEK."
    exit 1
fi
for tool_file in tools/codewarrior/mwcceppc.exe tools/codewarrior/mwasmeppc.exe; do
    [[ -f "$tool_file" ]] || { echo "Missing supplied compiler: $tool_file"; exit 1; }
done
mkdir -p logs
build_log=$(mktemp logs/build-linux-XXXXXXXX.log)
exec > >(tee "$build_log") 2>&1
if [[ -e build ]]; then
    mkdir -p build-history
    previous_build=$(mktemp -d build-history/run-XXXXXXXX)
    mv -- build "$previous_build/build"
fi
make -j4 all loader MKNITRO_SINGLE_CONFIG=0 CFLAGS= \
    "CC=$nitro_wibo ./tools/codewarrior/mwcceppc.exe" \
    "AS=$nitro_wibo ./tools/codewarrior/mwasmeppc.exe" \
    "KAMEK=$nitro_kamek" PYTHON=python3 SECURE=./external/not-bundled
python3 scripts/check_build_output.py
echo "Built isolated candidates. Read SOURCE_STATUS.md before runtime testing."
