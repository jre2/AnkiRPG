#-*- coding: utf-8 -*-
from   BattleCLI   import BattleCLI
from   Creatures   import mkCreatures
from   PlayerTests import *
from   Utils       import debug

class Player:
    PlayerTest = NoTest

    def __init__( self, names=None ):
        self.playerTest = self.PlayerTest()
        self.names = []
        if names: self.setCreatures( names )

    def setCreatures( self, names ):
        self.party = mkCreatures( names, cds= self.useCooldowns() )

    @property
    def isAlive( self ): return any( c.isAlive for c in self.party )

    def useCooldowns( self ): return self.playerTest.useCooldowns()

    def takeTurn( self, battle ):
        '''Handle assigning targets, activating specials, and performing player test
        This implies IO for rendering battle information and taking player input
        return test option color(s), if test passed, if AS should proc
        Note:
        User MAY assign suggested targets,
        MAY activate special skills,
        MUST choose color coded test option,
        MUST perform Player Test
        '''
        return ( [], False, False )

class HumanPlayer( Player ):
    PlayerTest = AnkiTest

    def takeTurn( self, battle ):
        cli = BattleCLI( self, battle )
        cli.cmdloop()
        return self.playerTest.doTest( cli.chosenTestOption )

class AIPlayer( Player ):
    PlayerTest = CooldownTest

    def takeTurn( self, battle ):
        #print battle.show( self )

        # activate specials ASAP
        for c in self.party:
            if c.isAlive and c.specialSkill and c.specialSkill.canActivate():
                c.specialSkill.onActivate()
                debug( 'ACTIVATE: %s' % c.idname )

        # choose test option randomly
        from random import choice
        optNum = choice( self.playerTest.testOptions.keys() )
        return self.playerTest.doTest( optNum )

class HumanNoTestPlayer( HumanPlayer ):
    PlayerTest = NoTest
class HumanCooldownTestPlayer( HumanPlayer ):
    PlayerTest = CooldownTest
class AINoTestPlayer( AIPlayer ):
    PlayerTest = NoTest
class AIAnkiTestPlayer( AIPlayer ):
    PlayerTest = AnkiTest
