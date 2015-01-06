#!/usr/bin/env python
#-*- coding: utf-8 -*-

from   Adventures import *
from   Config     import TEST_TYPE
from   Creatures  import *

def main():
    party = mkCreatures([ 'Alice', 'Alice', 'Bob', 'Bob', 'Casey', 'David' ], cds= TEST_TYPE == 'NoTest' )
    #a = Adventure( party )
    #a = SingleBattleAdventure( party )
    a = ThreeTrashAndBossAdventure( party )
    a.run()

if __name__ == '__main__': main()
