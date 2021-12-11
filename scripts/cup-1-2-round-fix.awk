#!/bin/awk


BEGIN {
    numMatches = 0
    numGames = 0
    prevEvent = ""
}

{
    if (/^\[Event [^]]*\]$/)
    {
	if (prevEvent != $0)
	{
	    ++numMatches
	    numGames = 0
	    prevEvent = $0
	}
	print
    }
    else if (/^\[Round [^]]*\]$/)
    {
	++numGames
	printf "[Round \"%d.%d\"]\n", numMatches, numGames
    }
    else
    {
	print
    }
}
