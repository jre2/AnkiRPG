#-*- coding: utf-8 -*-
class Skill:
    def __init__( self, **kwargs ):
        '''All kwargs become attributes of the skill'''
        self.kwargs = kwargs
        for k,v in kwargs.items():
            setattr( self, k, v )

        # these are reset for charged skills; they're more like 'num proced since last use'
        self._numASproced = 0
        self._numASprocedInARow = 0

    def new( self, owner ):
        '''Creature instances use this to create a new instance of the skill'''
        dup = self.__class__( **self.kwargs )
        dup.me = owner
        return dup

    def update( self, correct, asProced, acting ):
        '''Track whether test passed, whether it was sufficient to proc onAnswer skills, and whether the creature this skill belongs to is acting this round'''
        if acting and correct and asProced:
            self._numASproced += 1
            self._numASprocedInARow += 1

        if not correct:
            self._numASprocedInARow -= 1

    def __str__( self ):
        specialCharged = '!' if self.canActivate() else ''
        return '<%s%s:%s>' % ( specialCharged, self.__class__.__name__, self.kwargs )

    def onAnswer( self ):
        '''This hook runs before attack phase, iff test results proced Answer Skills'''
        pass

    def onAttack( self, targ ):
        '''This hook runs as attack happens, iff test results proced Answer Skills.
        return 'dont run default' to prevent standard attack from happening afterwards'''

    def canActivate( self ):
        '''This is checked during user REPL; no side-effects allowed'''
        return False

    def onActivate( self ):
        '''This hook runs when user requests; return False if no effect'''
        pass
