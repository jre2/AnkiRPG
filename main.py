#!/usr/bin/env python
#-*- coding: utf-8 -*-
from   Adventures import *
from   Player     import *

def main():
    #p = AIPlayer( [ 'Alice', 'Alice', 'Bob', 'Bob', 'Casey', 'David' ] )
    p = HumanPlayer( [ 'Alice', 'Alice', 'Bob', 'Bob', 'Casey', 'David' ] )
    #p = HumanNoTestPlayer( [ 'Alice', 'Alice', 'Bob', 'Bob', 'Casey', 'David' ] )
    #p = AIAnkiTestPlayer( [ 'Alice', 'Alice', 'Bob', 'Bob', 'Casey', 'David' ] )

    #a = SingleBattleAdventure( p )
    a = ThreeTrashAndBossAdventure( p )
    a.run()

if __name__ == '__main__': main()
