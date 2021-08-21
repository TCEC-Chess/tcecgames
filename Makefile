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

.PHONY: all clean distclean fetch-default-eco-pgn

# default target
all:

MAKEFILE-GEN := out/generated.mak

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(MAKECMDGOALS),distclean)

# generated rules
include $(MAKEFILE-GEN)

all: all-full-seasons all-full-tournaments all-full-events

all: all-compact-seasons all-compact-tournaments all-compact-events

endif
endif

$(MAKEFILE-GEN): master-archive/gamelist.json scripts/processgamelistjson.py
	mkdir -p out
	python -OO -m compileall scripts
	python -OO scripts/run-process-gamelist-json.py \
		--master-dir=master-archive \
		--generate-makefile master-archive/gamelist.json \
		> $(MAKEFILE-GEN)

clean:
	$(RM) -r out scripts/__pycache__

distclean: clean
	$(RM) eco.pgn

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
	python -OO scripts/run-compactify-pgn.py $< >$@
