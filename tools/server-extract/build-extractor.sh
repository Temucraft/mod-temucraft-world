#!/bin/sh
# Builds a map_extractor that also opens patch-6 ... patch-99 (the stock one stops at patch-5), without changing the
# core repository: the change is made, the tool is built, and the file is put back.
# usage: sh build-extractor.sh <core source folder> <core build folder>
# result: <build>/bin/map_extractor-all-patches
set -e
SRC=$1; BUILD=$2
[ -f "$SRC/src/tools/map_extractor/System.cpp" ] && [ -d "$BUILD" ] || { echo "usage: $0 <core source> <core build>"; exit 1; }
F="$SRC/src/tools/map_extractor/System.cpp"
cp "$F" "$F.temucraft-orig"
trap 'mv -f "$F.temucraft-orig" "$F"' EXIT
python3 - "$F" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
old = '''        sprintf(filename, "%s/Data/%s", input_path, CONF_mpq_list[i]);
        if (FileExists(filename))
            new MPQArchive(filename);
    }
'''
add = '''    // Temucraft: also every numbered patch after patch-5, up to 99 (make-client-tree.sh numbers the letter patches)
    for (int i = 6; i <= 99; ++i)
    {
        sprintf(filename, "%s/Data/patch-%d.MPQ", input_path, i);
        if (FileExists(filename))
            new MPQArchive(filename);
    }
'''
assert old in s, "map_extractor changed: tell Claude"
open(p, "w").write(s.replace(old, old + add, 1))
PY
cmake --build "$BUILD" --target map_extractor -j"$(nproc)"
# the binary is in bin/ or, in some build layouts, src/tools/map_extractor/
for f in "$BUILD/bin/map_extractor" "$BUILD/src/tools/map_extractor/map_extractor" "$BUILD/src/tools/map_extractor"; do
    if [ -f "$f" ] && [ -x "$f" ]; then mkdir -p "$BUILD/bin"; cp "$f" "$BUILD/bin/map_extractor-all-patches"; break; fi
done
[ -x "$BUILD/bin/map_extractor-all-patches" ] || { echo "map_extractor not found under $BUILD"; exit 1; }
echo "Built $BUILD/bin/map_extractor-all-patches"
