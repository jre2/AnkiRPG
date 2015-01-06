#-*- coding: utf-8 -*-
from   Skill import Skill

class BuffSelf( Skill ): # BuffParams
    def onAnswer( self ):
        self.me.addBuff( self.me, self.kwargs )

class BuffSameType( Skill ): # BuffParams
    def onAnswer( self ):
        for a in self.me.allies:
            if a.atkType == self.me.atkType and a.isAlive:
                a.addBuff( self.me, self.kwargs )

class ElementalSlayer( Skill ): # slayerMult
    def onAttack( self, targ ):
        if self.me.calcDmgMult( targ.atkType ) > 1: # if super effective
            targ.takeDamage( self.me.atk * self.slayerMult, self.me.atkType )
            return 'dont run default'

class UndividedAOE( Skill ): # aoeMult
    def onAttack( self, targ ):
        es = [ e for e in self.me.enemies if e.isTargettable ]
        dmg = self.me.atk * self.aoeMult
        for e in es:
            e.takeDamage( dmg, self.me.atkType )
        return 'dont run default'

class DividedAOE( Skill ): # aoeMult
    def onAttack( self, targ ):
        es = [ e for e in self.me.enemies if e.isTargettable ]
        if es:
            dmg = self.me.atk / len( es ) * self.aoeMult
            for e in es:
                e.takeDamage( dmg, self.me.atkType )
            return 'dont run default'

class NukeAfterNAnswered( Skill ): # nukeMult, N
    def onAttack( self, targ ):
        if self._numASproced >= self.N:
            self._numASproced = 0

            dmg = self.me.atk * nukeMult
            targ.takeDamage( dmg, self.me.atkType )
            return 'dont run default'

class NukeAfterNAnsweredInARow( Skill ): # nukeMult, N
    def onAttack( self, targ ):
        if self._numASprocedInARow >= self.N:
            self._numASprocedInARow = 0

            dmg = self.me.atk * nukeMult
            targ.takeDamage( dmg, self.me.atkType )
            return 'dont run default'

class BuffSelfAfterN( Skill ): # BuffParams, N
    def onAnswer( self ):
        if self._numASproced >= self.N:
            self._numASproced = 0

            self.me.addBuff( self.me, self.kwargs ) # this includes N, which is okay but annoying... could remove it if we care

class NukeSingle( Skill ): # nukeMult, N
    def canActivate( self ): return self._numASproced >= self.N
    def onActivate( self ):
        dmg = self.me.atk * self.nukeMult
        e = self.me.getTarget()
        if e:
            e.takeDamage( dmg, self.me.atkType )
            self._numASproced = 0
        else:
            return False

class NukeAOE( Skill ): # nukeMult, N
    def canActivate( self ): return self._numASproced >= self.N
    def onActivate( self ):
        dmg = self.me.atk * self.nukeMult
        es = [ e for e in self.me.enemies if e.isTargettable ]
        for e in es:
            e.takeDamage( dmg, self.me.atkType )
        else:
            return False
        self._numASproced = 0

class PassiveBuffSelf( Skill ): # BuffParams
    def onPassive( self ):
        self.me.addBuff( self.me, self.kwargs )

class PassiveBuffSameType( Skill ): # BuffParams
    def onPassive( self ):
        for a in self.me.allies:
            if a.atkType == self.me.atkType and a.isAlive:
                a.addBuff( self.me, self.kwargs )

MagicMissile = NukeSingle
