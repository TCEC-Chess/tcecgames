#!/bin/awk

BEGIN { commentLine = 0 }

{
    if (!commentLine || $0 != "")
	print

    if (/^\{[^}]*}$/)
        commentLine = 1
    else
	commentLine = 0;
}

