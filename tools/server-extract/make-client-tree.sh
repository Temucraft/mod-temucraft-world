#!/bin/sh
# Builds a client folder for the map extractors on the server out of the launcher files (no copies: symlinks).
# The launcher files are laid out for download (base/, patches/, locales/<locale>/); the extractors want a client
# (Data/, Data/enUS/). The extractors only open numbered patches, so the letter patches get numbers here, in the
# order the client loads them: patch-4 ... patch-8 keep their numbers, then patch-A = patch-9, patch-B = patch-10 ...
#
# usage: sh make-client-tree.sh [launcher files folder] [tree folder]
#        defaults: /var/www/wow-files  /srv/wow-client
set -e
FILES=${1:-/var/www/wow-files}
TREE=${2:-/srv/wow-client}
[ -d "$FILES/base/Data" ] || { echo "no $FILES/base/Data"; exit 1; }
if [ -e "$TREE" ] && [ ! -f "$TREE/.temucraft-client-tree" ]; then
    echo "$TREE exists and was not made by this script: pick another folder"; exit 1
fi
mkdir -p "$TREE"
touch "$TREE/.temucraft-client-tree"
# start again from empty: the tree only holds symlinks and the list
find "$TREE" -mindepth 1 -type l -delete
mkdir -p "$TREE/Data/enUS"
LIST="$TREE/patch-numbers.txt"
: > "$LIST"

for f in "$FILES"/base/Data/*.MPQ; do ln -s "$f" "$TREE/Data/$(basename "$f")"; done
n=4
for f in $(ls "$FILES"/patches/patch-*.MPQ | LC_ALL=C sort); do
    ln -s "$f" "$TREE/Data/patch-$n.MPQ"
    echo "Data/patch-$n.MPQ = patches/$(basename "$f")" >> "$LIST"
    n=$((n + 1))
done

for f in "$FILES"/base/Data/enUS/*.MPQ; do ln -s "$f" "$TREE/Data/enUS/$(basename "$f")"; done
n=4
for f in $(ls "$FILES"/locales/enUS/patch-enUS-*.MPQ 2>/dev/null | LC_ALL=C sort); do
    ln -s "$f" "$TREE/Data/enUS/patch-enUS-$n.MPQ"
    echo "Data/enUS/patch-enUS-$n.MPQ = locales/enUS/$(basename "$f")" >> "$LIST"
    n=$((n + 1))
done
echo "Client tree ready in $TREE (numbers in $LIST)."
