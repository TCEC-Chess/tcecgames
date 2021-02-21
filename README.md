TCEC Games Archive
==================

This is the TCEC games master PGN archive. Games are played at
[tcec-chess.com](https://tcec-chess.com/)


Archive maintenance scripts
---------------------------

The following archive maintenance scripts are provided:

 * scripts/fetch-update-gamelist.sh –
   Script that simply fetches the current version of gamelist.json
   (master game index) from the TCEC web server. The file is stored in
   master-archive/gamelist.json.
 * scripts/process-gamelist-json.py –
   The main maintenance script for fetching new PGN files from the
   TCEC web server.

The typical archive update procedure is:

    # update master game index
    scripts/fetch-update-gamelist.sh

    # fetch new PGNs
    scripts/process-gamelist-json.py --master-dir=master-archive --sync-from-web master-archive/gamelist.json

    # check that everything is ok
    scripts/process-gamelist-json.py --master-dir=master-archive --pgn-check -v master-archive/gamelist.json


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
