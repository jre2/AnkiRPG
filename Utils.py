#-*- coding: utf-8 -*-
import ext.colorama; ext.colorama.init() # this makes termcolor work on windows
from   ext.termcolor import colored, cprint
from   operator import mul

################################################################################
## Non-program specific utilities and hofs
################################################################################
def product( xs ): return reduce( mul, xs, 1 )

def weightedChoice( cws ): # [(Choice,Weight)] -> Rand Choice
    from random import random
    from bisect import bisect

    values, weights = zip(*cws)
    total = 0
    cum_weights = []
    for w in weights:
        total += w
        cum_weights.append(total)
    x = random() * total
    i = bisect(cum_weights, x)
    return values[i]

def debug( txt ): print colored( txt, 'white', 'on_blue' )
