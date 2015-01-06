#-*- coding: utf-8 -*-
from   BattleCLI import BattleCLI
from   Config    import DEBUG_NON_INTERACTIVE
from   Utils     import colored, cprint, debug, weightedChoice

class Battle:
    def __init__( self, allies, enemies, testType, battleNumber=1 ):
        self.battleNumber = battleNumber
        self.numRounds = 0
        self.testOptions = {1:None, 2:None, 3:None, 4:None }
        self.testType = testType
        self.allies  = allies
        self.enemies = enemies

        self.preBattle()

    def show( self ):
        '''Render battle status to string'''
        banner = ( ' Battle %d - Round %d ' % ( self.battleNumber, self.numRounds ) ).center( 80, '#' )
        opts = ' '.join( '%d %s' % x for x in self.testOptions.iteritems() )
        return '\n'.join([
              colored( banner, 'magenta' )
            , '\n'.join( c.showBrief() for c in self.enemies )
            , colored( '-'*40, 'magenta' )
            , '\n'.join( c.showDetailed() for c in self.allies )
            , colored( '-'*40, 'magenta' )
            , colored( opts, 'cyan' )
            , ''
            ])

    ##### State
    @property
    def isLost( self ): return all( not c.isAlive for c in self.allies )
    @property
    def isWon( self ):  return all( not c.isAlive for c in self.enemies )
    @property
    def isOver( self ): return self.isWon or self.isLost

    ##### Test Options
    def _refillTestOptions( self ):
        for k,v in self.testOptions.items():
            if not v:
                self.testOptions[k] = self._mkTestOption()

    def _mkTestOption( self ): return weightedChoice( [ ('Fire',25), ('Water',25), ('Lightning',25), ('Fire/Water',7), ('Fire/Lightning',7), ('Water/Lightning',7), ('Fire/Water/Lightning',4) ] )

    ##### Pre-battle
    def preBattle( self ):
        '''Perform pre-battle initialization (eg. clear buffs) and reapply passives'''
        for c in self.allies + self.enemies:
            c.preBattleInit()

        for c in self.allies + self.enemies:
            c.doPassives()

    ##### Post-battle
    def postBattle( self ):
        '''Report stats like kills, drops, persist/reset creature hp/charges etc as needed'''
        print self.show()

        if self.isWon:
            cprint( 'All enemies are defeated', 'green' )
        if self.isLost:
            cprint( 'All allies are defeated', 'red' )

    ##### Battle
    def nonInteractiveREPL( self ):
        '''Show status, activate specials asap, choose test option randomly'''
        print self.show()

        # activate specials asap
        for c in self.allies:
            if c.isAlive and c.specialSkill and c.specialSkill.canActivate():
                c.specialSkill.onActivate()
                debug( 'ACTIVATE: %s' % c.idname )

        # choosen test option randomly
        from random import randint
        n = randint( 1, 4 )

        chosenOption = self.testOptions[ n ]
        self.testOptions[ n ] = None
        debug( 'OPTION: %s' % chosenOption )
        return chosenOption

    def interactiveREPL( self ):
        '''Interactive CLI for player to operate displaying status, activating
        specials, and choosing test options'''
        cli = BattleCLI( self )
        cli.cmdloop()
        return cli.chosenOption

    def run( self ):
        '''Run battle step() until one side is defeated'''
        while not self.isOver:
            self.step()
        self.postBattle()

    def step( self ):
        '''Execute a single round of battle
        1. pre-round book keeping
        2. generate color coded categories
        3. user MAY assign suggested targets
        4. user MAY activate user-activated abilities
        5. user MUST choose color coded category
        6. user MUST perform user-test (eg. flashcard review). result :: (Success?, ProcAnswerSkill?)
        7. resolve combat round based on user-test result
        8. post-round book keeping
        '''
        # 1. pre-round book keeping
        for c in self.allies:   c.preRoundUpdate( self.allies, self.enemies )
        for c in self.enemies:  c.preRoundUpdate( self.enemies, self.allies )

        # 2. (re)generate test options
        self._refillTestOptions()

        # 3-5. handle user target suggestion, SS activation, and test option selection
        if DEBUG_NON_INTERACTIVE:   chosenOption = self.nonInteractiveREPL()
        else:                       chosenOption = self.interactiveREPL()

        # 6. user-test
        testPassed = True
        testProcedAnswerSkill = True
        #TODO: launch/control external Anki instance to review a card and get feedback
            # modify the above if applicable
        if self.testType == 'Anki': pass

        # 7. resolve combat
            # figure out which creatures get to act
        actingAllies  = [ c for c in self.allies if c.canAttack and c.atkType in chosenOption ]
        actingEnemies = [ c for c in self.enemies if c.canAttack ]
        acting        = actingAllies + actingEnemies

            # update creatures with test results (eg. for skill charges)
        for c in self.allies:   c.testUpdate( testPassed, testProcedAnswerSkill, c in acting )
        for c in self.enemies:  c.testUpdate( True, True, c in acting )

            # for those that get to, proc onAnswer and then attack with them
        for c in actingAllies:  c.onAnswer()
        for c in actingAllies:  c.doAttack( testProcedAnswerSkill )

            # if enemy could use specials/manually target (eg. multiplayer), they'd use them now
        for c in actingEnemies: c.onAnswer()
        for c in actingEnemies: c.doAttack( True )

        # 8. post-round book keeping
        self.numRounds += 1
