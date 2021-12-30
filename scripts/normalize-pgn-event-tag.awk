#!/bin/awk

BEGIN {
    currentEventTag = ""
    currentSubEvent = 0
    subEventTage = ""
}

END {
    if (currentSubEvent != numSubEvents) {
	printf("Number of provided subevents (%d) does not match with the number of observed subevents (%d)\n",
	       numSubEvents, currentSubEvent) > "/dev/stderr"
	exit 1
    }
}

{
    if (/^\[Event "[^]]*"[]]$/) {

	event_tag = substr($0, 9, length($0) - 10)

	if (event_tag != currentEventTag) {
	    ++currentSubEvent
	    currentEventTag = event_tag

	    if (currentSubEvent != 1 && numSubEvents < 2) {
		print "This PGN has sub-events but numSubEvents is not 2 or above" > "/dev/stderr"
		exit 1
	    }

	    if (numSubEvents < 2) {
		subEventTag = ""
	    } else {
		subEventTag = sprintf("%c", 96 + currentSubEvent)
	    }
	}

	sub("^TCEC ", "", event_tag)
	sub("^Season [[:digit:]]+", "", event_tag)
	sub("^[[:space:]]*[-][[:space:]]*", "", event_tag)

	printf "[Event \"TCEC Season %02u (%02u%s) %s\"]\n", season, eventNumber, subEventTag, event_tag

    } else {
	print
    }
}
