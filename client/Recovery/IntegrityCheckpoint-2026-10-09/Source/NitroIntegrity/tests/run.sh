#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
test_output_dir="$(mktemp -d)"
trap 'rm -rf "$test_output_dir"' EXIT
python3 tests/test_manifest.py
"${CXX:-g++}" -std=c++98 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer -g -I../PulsarEngine tests/test_policy.cpp -o "$test_output_dir/policy"
ASAN_OPTIONS=detect_leaks=0 "$test_output_dir/policy"
for enforcement in 0 1; do
    "${CXX:-g++}" -std=c++98 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer -g -DMKNITRO_AC_ENFORCE_INTEGRITY="$enforcement" -Itests/mocks -I../PulsarEngine tests/test_adapter.cpp -o "$test_output_dir/adapter_$enforcement"
    ASAN_OPTIONS=detect_leaks=0 "$test_output_dir/adapter_$enforcement"
done

# Reviewed baseline is a temporary host fixture only; never edit production approval.
mkdir -p "$test_output_dir/reviewed/Security/NitroIntegrity"
sed 's/ManifestRuntimeReviewed = false/ManifestRuntimeReviewed = true/' \
    ../PulsarEngine/Security/NitroIntegrity/Manifest.hpp \
    > "$test_output_dir/reviewed/Security/NitroIntegrity/Manifest.hpp"
"${CXX:-g++}" -std=c++98 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer -g \
    -DMKNITRO_AC_ENFORCE_INTEGRITY=1 -I"$test_output_dir/reviewed" -Itests/mocks -I../PulsarEngine \
    tests/test_adapter.cpp -o "$test_output_dir/reviewed_adapter"
ASAN_OPTIONS=detect_leaks=0 "$test_output_dir/reviewed_adapter"
