#-*- coding: utf-8 -*-
from   Adventure import Adventure
from   Creatures import mkCreature, mkCreatures

class SingleBattleAdventure( Adventure ):
    def getNextEncounter( self ):
        yield mkCreatures([ 'Alice', 'Charlie', 'David' ], cds= True )

class ThreeTrashAndBossAdventure( Adventure ):
    def getNextEncounter( self ):
        yield mkCreatures([ 'Alice', 'Alice' ], cds= True )
        yield mkCreatures([ 'Bob', 'Bob' ], cds= True )
        yield mkCreatures([ 'Alice', 'Bob', 'Charlie' ], cds= True )
        yield mkCreatures([ 'Alice', 'Boss', 'Charlie', 'David' ], cds= True )
