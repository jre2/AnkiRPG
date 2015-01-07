#-*- coding: utf-8 -*-
from   Adventure import Adventure
from   Player    import AIPlayer

class SingleBattleAdventure( Adventure ):
    def getNextEncounter( self ):
        yield AIPlayer([ 'Alice', 'Charlie', 'David' ])

class ThreeTrashAndBossAdventure( Adventure ):
    def getNextEncounter( self ):
        yield AIPlayer([ 'Alice', 'Alice' ])
        yield AIPlayer([ 'Bob', 'Bob' ])
        yield AIPlayer([ 'Alice', 'Bob', 'Charlie' ])
        yield AIPlayer([ 'Alice', 'Boss', 'Charlie', 'David' ])
