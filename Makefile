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

# targets for creating the release
.PHONY: release release-recreate-dir release-md5sum
.PHONY: release-full-seasons release-full-tournaments release-full-events
.PHONY: release-compact-seasons release-compact-tournaments release-compact-events release-compact-everything

# default target
all: all-pgns

MAKEFILE-GEN := out/generated.mak

# include generated rules, but only if we're not cleaning
ifneq ($(MAKECMDGOALS),clean)
ifneq ($(MAKECMDGOALS),distclean)

# all pgns
all-pgns: all-full-seasons all-full-tournaments all-full-events

all-pgns: all-compact-seasons all-compact-tournaments all-compact-events

all-pgns: out/compact/everything/TCEC-everything.pgn

# generated rules
include $(MAKEFILE-GEN)

endif
endif

# generated rules
$(MAKEFILE-GEN): master-archive/gamelist.json scripts/processgamelistjson.py
	mkdir -p out
	python3 -OO -m compileall scripts
	python3 -OO scripts/run-process-gamelist-json.py \
		--master-dir=master-archive \
		--generate-makefile master-archive/gamelist.json \
		> $(MAKEFILE-GEN)

clean:
	$(RM) -r out scripts/__pycache__

distclean: clean
	$(RM) eco.pgn

fetch-gamelist-json:
	scripts/fetch-update-gamelist.sh

fetch-new-pgns:
	python3 scripts/run-process-gamelist-json.py --master-dir=master-archive --sync-from-web master-archive/gamelist.json
	python3 scripts/run-process-gamelist-json.py --master-dir=master-archive --pgn-check -v master-archive/gamelist.json
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
out/compact/events/%.pgn: out/full/events/%.pgn
	mkdir -p out/compact/events
	python3 -OO scripts/run-compactify-pgn.py $< >$@


# release
RELEASE-DIR=release-$(shell date -u +"%Y-%m-%d")-$(shell git rev-parse --short HEAD)

release: release-md5sum

release-md5sum:
	mkdir -p out/$(RELEASE-DIR)
	cd out; md5sum -b $$(find compact full/events -type f | sort) > $(RELEASE-DIR)/MD5SUM

release: release-full-events

release: release-compact-seasons release-compact-tournaments release-compact-events release-compact-everything

release-full-seasons:
	mkdir -p out/$(RELEASE-DIR)
	cd out; zip -q -9 -r $(RELEASE-DIR)/TCEC-seasons-full.zip full/seasons

release-full-tournaments:
	mkdir -p out/$(RELEASE-DIR)
	cd out; zip -q -9 -r $(RELEASE-DIR)/TCEC-tournaments-full.zip full/tournaments

release-full-events:
	mkdir -p out/$(RELEASE-DIR)
	cd out; 7z a -bd -mx=9 -ms=on $(RELEASE-DIR)/TCEC-events-full.7z full/events

release-compact-seasons:
	mkdir -p out/$(RELEASE-DIR)
	cd out; zip -q -9 -r $(RELEASE-DIR)/TCEC-seasons-compact.zip compact/seasons

release-compact-tournaments:
	mkdir -p out/$(RELEASE-DIR)
	cd out; zip -q -9 -r $(RELEASE-DIR)/TCEC-tournaments-compact.zip compact/tournaments

release-compact-events:
	mkdir -p out/$(RELEASE-DIR)
	cd out; zip -q -9 -r $(RELEASE-DIR)/TCEC-events-compact.zip compact/events

release-compact-everything:
	mkdir -p out/$(RELEASE-DIR)
	cd out; zip -q -9 -r $(RELEASE-DIR)/TCEC-everything-compact.zip compact/everything
