#-*- coding: utf-8 -*-
class Skill:
    def __init__( self, **kwargs ):
        self.kwargs = kwargs
        for k,v in kwargs.items():
            setattr( self, k, v )

        # these are reset for charged skills; they're more like 'num proced since last use'
        self._numASproced = 0
        self._numASprocedInARow = 0

    def new( self, owner ):
        '''Creature instances use this to create a new instance of the skill'''
        from copy import copy
        s = copy( self )
        s.me = owner
        return s

    def update( self, correct, asProced, acting ):
        if acting and correct and asProced:
            self._numASproced += 1
            self._numASprocedInARow += 1

        if not correct:
            self._numASprocedInARow -= 1

    def __str__( self ):
        specialCharged = '!' if self.canActivate() else ''
        return '<%s%s:%s>' % ( specialCharged, self.__class__.__name__, self.kwargs )

    # this hook runs before attack phase iff proced
    def onAnswer( self ): pass
    # this hook runs as attack happens iff proced
    def onAttack( self, targ ): pass

    # this is checked during user REPL; no side-effects allowed
    def canActivate( self ): return False
    # this hook runs when user requests; return False if no effect
    def onActivate( self ): pass
