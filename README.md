TCEC Games Archive
==================

This is the TCEC games master PGN archive. Games are played at
[tcec-chess.com](https://tcec-chess.com/)


Releases
--------

See the [Releases page](https://github.com/TCEC-Chess/tcecgames/releases/)
for the official releases.

The TCEC games are released both in full and compacted formats:

- The full format has all the original engine evaluation comments.

- The compacted format replaces all comments with book exit
  markers. The compacted format also reclassifies the openings and
  their ECO codes for better consistency.

If in doubt, choose the compacted format.

The original PGNs are also available as a download ("Source code"
links in releases) and by cloning the git repository.

Please report any issues at the
[TCEC Official discord](https://discord.gg/EYuyrDr)
channel \#enginedev-lobby.

Archive maintenance
-------------------

Archive maintenance is performed through the top-level Makefile.

The typical archive update procedure is:

    # update master game index
    make fetch-gamelist-json

    # fetch new PGNs
    make fetch-new-pgns

    # regenerate outputs
    make clean && make -j all

    # create release packages
    make -j release

    # test the release packages
    make -j test-release

License
-------

All scripts (i.e., anything that does not end in .pgn) are released
under the Apache License 2.0:

    Copyright 2021 Top Chess Engine Championship organization

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.


The PGN game files are released under the [Creative Commons BY-SA 3.0
license](https://creativecommons.org/licenses/by-sa/3.0/legalcode).


Credits
-------

The archive is maintained by the TCEC organization. You may reach us
at the [TCEC Official discord](https://discord.gg/EYuyrDr) channel
\#enginedev-lobby.

The credits for the awesome games go to the awesome chess engines
participating in the TCEC events.
