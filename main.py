#!/usr/bin/env python
#-*- coding: utf-8 -*-

from   Adventures import *
from   Config     import TEST_TYPE
from   Player     import *
from   Creatures  import *

def main():
    #p = AIPlayer( [ 'Alice', 'Alice', 'Bob', 'Bob', 'Casey', 'David' ] )
    #a = ThreeTrashAndBossAdventure( p )
    p = HumanPlayer( [ 'Alice', 'Alice', 'Bob', 'Bob', 'Casey', 'David' ] )
    a = SingleBattleAdventure( p )
    a.run()

if __name__ == '__main__': main()
