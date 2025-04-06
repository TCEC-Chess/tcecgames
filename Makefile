# Copyright 2021 Top Chess Engine Championship organization
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

.PHONY: all clean distclean fetch-default-eco-pgn fetch-gamelist-json fetch-new-pgns all-pgns
.PHONY: enumerate-events

# targets for creating the release
.PHONY: release release-dir release-md5sum release-changelog
.PHONY: release-full-seasons release-full-tournaments release-full-events
.PHONY: release-compact-seasons release-compact-tournaments release-compact-events release-compact-everything release-compact-everything-compet-traditional
.PHONY: release-compact-all-in-one

# target for testing the release packages
.PHONY: test-release

# default target
all: all-pgns scripts/gen-all-engines.txt

MAKEFILE-GEN := out/generated.mak

GAMELIST-JSONS := master-archive/gamelist.json scripts/gamelist-overlay.json

PYTHON3 := python-venv/bin/python3

# include generated rules, but only if we're not cleaning
ifneq ($(MAKECMDGOALS),clean)
ifneq ($(MAKECMDGOALS),distclean)

# all pgns
all-pgns: all-full-seasons all-full-tournaments all-full-events

all-pgns: all-compact-seasons all-compact-tournaments all-compact-events

all-pgns: out/compact/everything/TCEC-everything.pgn
all-pgns: out/compact/everything/TCEC-everything-compet-traditional.pgn
all-pgns: out/compact/everything/TCEC-everything-compet-frc.pgn
all-pgns: out/compact/everything/TCEC-everything-compet-dfrc.pgn
all-pgns: out/compact/everything/TCEC-everything-bonus-test.pgn

# generated rules
include $(MAKEFILE-GEN)

endif
endif

$(PYTHON3):
	python3 -m venv python-venv
	python-venv/bin/pip3 install python-chess

# generated rules
$(MAKEFILE-GEN): $(GAMELIST-JSONS) scripts/processgamelistjson.py $(PYTHON3)
	mkdir -p out
	$(PYTHON3) -OO -m compileall scripts
	$(PYTHON3) -OO scripts/run-process-gamelist-json.py \
		--master-dir=master-archive \
		--generate-makefile $(GAMELIST-JSONS) \
		> $(MAKEFILE-GEN)

clean:
	$(RM) -r out scripts/__pycache__

distclean: clean
	$(RM) eco.pgn
	$(RM) -r python-venv

enumerate-events: $(PYTHON3)
	$(PYTHON3) scripts/run-process-gamelist-json.py --master-dir=master-archive -v $(GAMELIST-JSONS)

fetch-gamelist-json:
	scripts/fetch-update-gamelist.sh

fetch-new-pgns: $(PYTHON3)
	$(PYTHON3) scripts/run-process-gamelist-json.py --master-dir=master-archive --sync-from-web $(GAMELIST-JSONS)
	$(PYTHON3) scripts/run-process-gamelist-json.py --master-dir=master-archive --pgn-check -v $(GAMELIST-JSONS)
	$(RM) $(MAKEFILE-GEN)

fetch-default-eco-pgn:
	wget --output-document=eco.pgn https://www.cs.kent.ac.uk/~djb/pgn-extract/eco.pgn

eco.pgn:
	@echo "Use the following command to fetch the default ECO classification book:"
	@echo
	@echo "    make fetch-default-eco-pgn"
	@echo
	@exit 1

# compact event pgns
out/compact/events/%.pgn: out/full/events/%.pgn $(PYTHON3)
	mkdir -p out/compact/events
	$(PYTHON3) -OO scripts/run-compactify-pgn.py $< >$@

scripts/gen-all-engines.txt: out/compact/everything/TCEC-everything.pgn
	echo "# This is a generated file." >$@
	echo >>$@
	egrep '^\[(White|Black) "[^"]*"\]$$' $< | \
		sed -e 's/^........//' -e 's/..$$//' | \
		sort -u >>$@

# release
RELEASE-DIR := releases/release-$(shell date -u +"%Y-%m-%d")-$(shell git rev-parse --short HEAD)

release: release-md5sum release-changelog

release-dir:
	mkdir -p $(RELEASE-DIR)

release-md5sum: release-dir
	cd out; md5sum -b $$(find compact/everything full/events -type f | sort) > ../$(RELEASE-DIR)/MD5SUM

release-changelog: release-dir
	cp ChangeLog.txt $(RELEASE-DIR)/

release: release-full-events

release: release-compact-all-in-one release-compact-everything

release-full-seasons: release-dir
	cd out; zip -q -9 -r ../$(RELEASE-DIR)/TCEC-seasons-full.zip full/seasons

release-full-tournaments: release-dir
	cd out; zip -q -9 -r ../$(RELEASE-DIR)/TCEC-tournaments-full.zip full/tournaments

release-full-events: release-dir
	cd out; 7z a -bd -mx=9 -ms=on ../$(RELEASE-DIR)/TCEC-events-full.7z full/events

release-compact-seasons: release-dir
	cd out; zip -q -9 -r ../$(RELEASE-DIR)/TCEC-seasons-compact.zip compact/seasons compact/seasons-compet-traditional compact/seasons-compet-frc compact/seasons-compet-dfrc compact/seasons-bonus-test

release-compact-tournaments: release-dir
	cd out; zip -q -9 -r ../$(RELEASE-DIR)/TCEC-tournaments-compact.zip compact/tournaments

release-compact-events: release-dir
	cd out; zip -q -9 -r ../$(RELEASE-DIR)/TCEC-events-compact.zip compact/events

release-compact-everything: release-dir
	cd out/compact/everything; zip -q -9 -r ../../../$(RELEASE-DIR)/TCEC-everything-compact.zip \
		TCEC-everything-compet-traditional.pgn \
		TCEC-everything-compet-frc.pgn \
		TCEC-everything-compet-dfrc.pgn \
		TCEC-everything-bonus-test.pgn

release-compact-all-in-one: release-dir
	cd out/compact/everything; zip -q -9 -r ../../../$(RELEASE-DIR)/TCEC-all-in-one-compact.zip \
		TCEC-everything.pgn
test-release:
	$(RM) -r out/tmp-release-unpack
	mkdir -p out/tmp-release-unpack
	cd out/tmp-release-unpack && mkdir -p compact/everything && cd compact/everything && unzip ../../../../$(RELEASE-DIR)/TCEC-everything-compact.zip
	cd out/tmp-release-unpack && mkdir -p compact/everything && cd compact/everything && unzip ../../../../$(RELEASE-DIR)/TCEC-all-in-one-compact.zip
	cd out/tmp-release-unpack && 7z x ../../$(RELEASE-DIR)/TCEC-events-full.7z
	cd out/tmp-release-unpack && md5sum --quiet -c ../../$(RELEASE-DIR)/MD5SUM
	@echo "Release packages OK"
	$(RM) -r out/tmp-release-unpack
