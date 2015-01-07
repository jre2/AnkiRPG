#-*- coding: utf-8 -*-
from   BattleCLI import BattleCLI
from   Config    import DEBUG_NON_INTERACTIVE
from   Utils     import colored, cprint, debug

#TODO: handle teams of players and victory conditions other than Last Man Standing

class Battle:
    def __init__( self, players, battleNumber=1 ):
        self.battleNumber = battleNumber
        self.numRounds = 0
        self.players = players

        self.preBattle()

    def show( self, povPlayer=None, povAtBottom=False ):
        '''Render battle status to string, and if specified, relative to a POV player.
        In that case, show more detail about them and change ordering of players'''
        def showPlayer( p ):
            if povPlayer == p: return '\n'.join( c.showDetailed() for c in p.party )
            else:              return '\n'.join( c.showBrief() for c in p.party )

        players = self.players
        if povAtBottom:
            players = [ p for p in self.players if p != povPlayer ] + [ p for p in self.players if p == povPlayer ]

        banner = colored( ( ' Battle %d - Round %d ' % ( self.battleNumber, self.numRounds ) ).center( 80, '#' ), 'magenta' )
        hline = colored( '-'*40, 'magenta' )
        parties = ('\n%s\n' % hline).join( showPlayer( p ) for p in players )
        return '\n'.join([
            banner,
            parties,
            hline,
            ])

    @property
    def isOver( self ): return 1 == len([ p for p in self.players if p.isAlive ]) # only 1 player alive
    @property
    def creatures( self ): return sum( ( [ c for c in p.party ] for p in self.players ), [] )

    def creatureById( self, cid ): return [ c for c in self.creatures if c.id == cid ][0]

    def preBattle( self ):
        '''Perform pre-battle initialization (eg. clear buffs) and reapply passives'''
        for p in self.players:
            for c in p.party:
                c.preBattleInit()

        for p in self.players:
            for c in p.party:
                c.doPassives()

    def postBattle( self ):
        '''Report stats like kills, drops, etc that aren't handled by adventure'''
        print self.show()

    def run( self ):
        '''Run battle step() until one side is defeated'''
        while not self.isOver:
            self.step()
        self.postBattle()

    def step( self ):
        '''Execute a single round of battle'''
        # update buffs, atk cooldowns, IFF
        for p in self.players:
            enemies = sum( ( p2.party for p2 in self.players if p != p2 ), [] )
            for c in p.party: c.preRoundUpdate( p.party, enemies )

        # have each player take turns
        for p in self.players:
            ( colors, testPassed, asProced ) = p.takeTurn( self )
            acting = [ c for c in p.party if c.canAttack and c.atkType in colors ]
            for c in p.party: c.testUpdate( testPassed, asProced, c in acting )
            for c in acting:  c.onAnswer()
            for c in acting:  c.doAttack( asProced )

        self.numRounds += 1
