# Map files on the server

The server's map, vmap and mmap files are made from the client's MPQs. The server only has the launcher files
(`/var/www/wow-files`: `base/`, `patches/`, `locales/<locale>/`), not a client folder, and the stock extractors only
open numbered patches (map_extractor stops at patch-5), while our maps are in letter patches (patch-V Forever maps,
patch-X Darkspear Islands, patch-Y / patch-Z Cataclysm and Mists maps).

1. **Client folder made of symlinks** (no copies, a few seconds):

       sh make-client-tree.sh /var/www/wow-files /srv/wow-client

   Data/ gets the base MPQs, and the patches renumbered in the order the client loads them
   (patch-4 ... patch-8 stay, then patch-A = patch-9, patch-B = patch-10 ...). The list is in
   `/srv/wow-client/patch-numbers.txt`. Run it again after every release upload that changes a patch.

2. **A map_extractor that opens patch-6 ... patch-99** (once, and after core updates):

       sh build-extractor.sh <core source folder> <core build folder>

   It changes `src/tools/map_extractor/System.cpp` only for the build and puts the file back; the result is
   `<build>/bin/map_extractor-all-patches`. vmap4_extractor already scans patch-2 ... patch-99.

3. **Extract** (in `/srv/wow-client`, then move the results into the server's data folder):

       cd /srv/wow-client
       <build>/bin/map_extractor-all-patches -e 1          # maps only (1 = maps; DBCs come from the server's own dbc)
       <build>/bin/vmap4_extractor -l && <build>/bin/vmap4_assembler Buildings vmaps
       <build>/bin/mmaps_generator <map id> --threads $(nproc)   # one map at a time, for the maps that changed

   Copy `maps/`, `vmaps/` and `mmaps/` over the server's (stop the worldserver first, keep a backup).
   map and vmap extraction always redo every map; mmaps can be limited to the maps that changed.
