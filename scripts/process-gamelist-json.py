#!/usr/bin/python3

import getopt
import json
import os.path
import re
import shutil
import sys
import urllib.request

# globals
verbose_output = False
dry_run = False
operating_mode = "ENUMERATE"
input_directory = None
master_directory = None

def help_and_exit():
    print('''Usage: process-gamelist-json.py [options] <gamelist.json>

Reads the TCEC game list json file and performs archive
maintenance. By default, the events are enumerated and classified to
stdout.

Options:
-h --help                    This help
-n --dry-run                 Dry run, don't write anything to the file system.
   --master-dir=<dir>        Master archive directory.
   --pgn-check               Check that all PGNs listed in gamelist.json exist.
   --sync-from-dir=<dir>     Add missing event PGNs to master-archive from
                             a directory.
   --sync-from-web           Add missing event PGNs to master-archive from
                             TCEC web site.
-v --verbose                 Enable verbose output
''')
    sys.exit(1)


def info(str):
    sys.stderr.write(f"{str}\n")

def verbose(str):
    if (verbose_output):
        sys.stderr.write(f"{str}\n")

def warning(str):
    sys.stderr.write(f"Warning: {str}\n")

def fatal(str, exitcode):
    sys.stderr.write(f"Fatal: {str} (exit={exitcode})\n")
    sys.exit(exitcode)

def sort_key_from_event(event):
    return event["dno"]

def classify_event(season, event_id, event_name):
    if season == "Bonus":
        return "BONUS"

    if "Cup" in season:
        return "CUP"

    if season.isdigit():
        if ("test" in event_id.lower()) or ("test" in event_name.lower()):
            return "TEST"

        if ("bonus" in event_id.lower()) or ("bonus" in event_name.lower()):
            return "BONUS"

        if "frc" in event_id.lower():
            return "FRC"

        # old style main event ids
        if re.fullmatch('s[0-9]{1,2}stage([0-9][a-z]|rapid)', event_id):
            return "MAIN"

        # the full variety of new style main event ids
        if re.fullmatch('s[0-9]{1,2}division([a-z]|[0-9]|sf|[0-9][a-z]|rapid|blitz|playoff|l[0-9]|ql|cpul1)',
                        event_id):
            return "MAIN"

        # special cases
        if event_id in ["s9rapid", "s15division4a4bplayoff", "s16divisionl1playoff", "s17divisionplayofffordivp"]:
            return "MAIN"

        if re.fullmatch('s[0-9]{1,2}stage([a-z]|[0-9])', event_id):
            return "MAIN"

        # if we get here, then everything that doesn't match above is bonus (up to S19)
        if int(season) <= 19:
            return "BONUS"

    warning(f"Don't know how to classify Season '{season}', event id 'event_id', event name 'event_name'")
    return "MISC"

def sync_pgn(pgnfile):
    # first, check that we have the master archive set
    if master_directory is None:
        fatal("Master directory not set", 3)

    if not os.path.isdir(master_directory):
        fatal(f"Not a directory: '{master_directory}'", 4)

    output_file = f"{master_directory}/{pgnfile}"


    if operating_mode == "SYNC-FROM-DIR":
        # check if we already have the file
        if os.path.isfile(output_file):
            return

        input_file = f"{input_directory}/{pgnfile}"
        if not os.path.isfile(input_file):
            warning(f"Input file not '{input_file}' not found")
            return

        info(f"{input_file} --> {output_file}")
        if not dry_run:
            shutil.copyfile(input_file, output_file)

    if operating_mode == "SYNC-FROM-WEB":
        # check if we already have the file
        if os.path.isfile(output_file):
            return

        input_url = f"https://tcec-chess.com/archive/json/{pgnfile}"

        info(f"{input_url} --> {output_file}")

        try:
            with urllib.request.urlopen(input_url) as f:
                pgncontent = f.read()
                if not dry_run:
                    outfile = open(output_file, "wb")
                    outfile.write(pgncontent)
                    outfile.close()

                f.close()

        except urllib.error.HTTPError:
            warning(f"Cannot fetch {input_url}: {sys.exc_info()[0]}")

    if operating_mode == "PGN-CHECK":
        if os.path.isfile(output_file):
            if os.stat(output_file).st_size == 0:
                info(f"Empty file: {output_file}")
                return

            # check whether the output is unicode
            f = open(output_file, "rb")
            try:
                f.read().decode('utf-8')
            except UnicodeDecodeError:
                info(f"Not an UTF-8 file: {output_file}")

            f.close()

        else:
            info(f"Missing: {output_file}")


def gamelist_to_master_index(gamelist):

    for season in gamelist["Seasons"]:
        verbose(f"Season '{season}'")

        for event in sorted(gamelist["Seasons"][season]["sub"], key=sort_key_from_event, reverse=True):
            event_id = event["id"]
            event_file_base = event["abb"]
            event_name = event["menu"]
            event_url = event["url"]

            # check whether we have everything we need
            if (event_id is None) or (event_file_base is None) or (event_name is None) or (event_url is None):
                continue

            # divider check
            if event_id.endswith("divider") or event_file_base.endswith("None"):
                continue

            # we'll ignore the current event
            if event_id == "current":
                continue

            event_class = classify_event(season, event_id, event_name)

            if operating_mode == "ENUMERATE":
                print(f"{event_id} {event_class} {event_file_base}.pgn '{event_name}'")

            if operating_mode in ("SYNC-FROM-DIR", "SYNC-FROM-WEB", "PGN-CHECK"):
                sync_pgn(f"{event_file_base}.pgn")

def main(argv):
    global verbose_output
    global dry_run
    global operating_mode
    global input_directory
    global master_directory

    inputfile = ''

    # version check -- this script was developed with Python 3.6
    if sys.version_info < (3, 6):
        warning(f"Python version {sys.version_info.major}.{sys.version_info.minor} is not at least 3.6!")

    try:
        opts, args = getopt.getopt(argv, "hvn",
                                   ["help", "verbose", "dry-run", "master-dir=", "pgn-check",
                                    "sync-from-dir=", "sync-from-web"])
        inputfile = args[0]
    except getopt.GetoptError:
        help_and_exit()
    except IndexError:
        help_and_exit()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            help_and_exit()
        if opt in ("-v", "--verbose"):
            verbose_output = True
        if opt in ("-n", "--dry-run"):
            dry_run = True
        if opt == "--master-dir":
            master_directory = arg
        if opt == "--sync-from-dir":
            operating_mode = "SYNC-FROM-DIR"
            input_directory = arg
        if opt == "--pgn-check":
            operating_mode = "PGN-CHECK"
        if opt == "--sync-from-web":
            operating_mode = "SYNC-FROM-WEB"

    try:
        gamefile = open(inputfile, 'r')
        gamelist = json.load(gamefile)
        gamefile.close()
        gamelist_to_master_index(gamelist)

    except FileNotFoundError:
        fatal(f"Game list JSON '{inputfile}' not found", 2)

if __name__ == "__main__":
    main(sys.argv[1:])
