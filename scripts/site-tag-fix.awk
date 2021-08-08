#!/bin/awk

BEGIN { numGames = 0 }

{
    if (/^\[Site [^]]*\]$/)
    {
	numGames++
	printf "[Site \"%s&game=%d\"]\n", urlprefix, numGames
    }
    else
    {
	print
    }
}
