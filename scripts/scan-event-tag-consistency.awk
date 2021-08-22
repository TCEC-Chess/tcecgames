#!/bin/awk

BEGIN { event_tag = "" }

{
    if (/^\[Event [^]]*[]]$/) {
	if (event_tag == "") {
	    event_tag = $0
	} else if (event_tag != $0 ) {
	    print "Inconsistent event tag! Expected: '" event_tag "' got '" $0 "'"
	    exit 1
	}
    }
}
