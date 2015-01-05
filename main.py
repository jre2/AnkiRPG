#!/usr/bin/env python
#-*- coding: utf-8 -*-
import itertools
from termcolor import colored, cprint
#import colorama; colorama.init() # this makes termcolor work on windows

'''TODO
REPL with player tagetting, SS activation, and category selection
Player quiz and result fetch
Creature skills and passives
Collection, creature progression (levels/evolutions), and deck mangement
'''

################################################################################
## Debug
################################################################################
DEBUG_TARGETTING = True

################################################################################
## Creature DB
################################################################################
CREATURE_DB = {
    'Alice':    ( 500, 250, 'Fire' ),
    'Bob':      ( 450, 300, 'Lightning', 2 ),
    'Charlie':  ( 550, 200, 'Water' ),
    }

################################################################################
## Battle board
################################################################################
class Battle:
    def __init__( self ):
        self.allies  = self.mkCreatures([ 'Alice', 'Alice', 'Charlie' ])
        self.enemies = self.mkCreatures([ 'Alice', 'Bob', 'Charlie' ])

        self.numRounds = 0

    def show( self ):
        banner = ( ' Round %d ' % self.numRounds ).center( 80, '#' )
        return '\n'.join([
              colored( banner, 'magenta' )
            , '\n'.join( c.showBrief() for c in self.enemies )
            , colored( '-'*40, 'magenta' )
            , '\n'.join( c.showDetailed() for c in self.allies )
            , ''
            ])

    def mkCreature( self, name ):   return Creature( name, *CREATURE_DB[ name ] )
    def mkCreatures( self, names ): return [ self.mkCreature( name ) for name in names ]

    def step( self ):
        '''
        0. generate color coded categories
        1. user MAY assign suggested targets
        2. user MAY activate user-activated abilities
        3. user MUST choose color coded category
        4. user MUST perform user-test (eg. flashcard review). result :: (Success?, ProcAnswerSkill?)
        5. resolve combat round based on user-test result
        6. post-round book keeping
        '''
        print self.show()
        #TODO: 0 generate category options
        #TODO: 0-3 CLI repl to handle user target suggestion and SS activation until category selection
        categories = ['Fire']

        #TODO: 4 user-test
        testResult = ( True, True ) # :: (Success?,ProcAnswerSkill?)

        # 5. resolve combat
        for c in self.allies:
            c.doAttack( self.enemies )

        for c in self.enemies:
            c.doAttack( self.allies )

        # 6. book keeping
        self.numRounds += 1

################################################################################
## Creature
################################################################################
class Creature:
    #TODO: check for buffs from skills and passives from self and allies
    ATTACK_TYPE_DAMAGE_MULT = {
            'Fire':         { 'Fire':1.0, 'Water':0.5, 'Lightning':1.5, },
            'Water':        { 'Fire':1.5, 'Water':1.0, 'Lightning':0.5, },
            'Lightning':    { 'Fire':0.5, 'Water':1.5, 'Lightning':1.0, },
            }
    NEXT_ID = itertools.count(0)
    def __init__( self, name, hp, atk, atkType, atkCooldown=1 ):
        self.name = name
        self.id = Creature.NEXT_ID.next()
        self.idname = '%d %10s' % ( self.id, '[%s]' % self.name )

        self._maxHP = hp
        self._curHP = hp
        self._hp_dmg_taken = 0

        self._atk = atk
        self.atkType = atkType
        self.atkCooldown = atkCooldown
        self.atkTTA      = atkCooldown # Turns Til next Attack

        self.answerSkill = None
        self.specialSkill = None

        self.suggestedTarget = None

    ##### Stats
    @property
    def atk( self ):    return self._atk
    @property
    def maxHP( self ):  return self._maxHP
    @property
    def curHP( self ):  return self.maxHP - self._hp_dmg_taken

    ##### State
    @property
    def isAlive( self ):        return self.curHP > 0
    @property
    def isTargettable( self ):  return self.isAlive

    ##### Damage and healing

    # receiver handles dmg mult (in case their skills modify things), but attack can use this to help
    def calcDmgMult( self, eType ): return Creature.ATTACK_TYPE_DAMAGE_MULT[ self.atkType ][ eType ]
    def calcDmg( self, eType ):     return self.atk * self.calcDmgMult( eType )

    def takeDamage( self, dmg, eType ):
        mult = Creature.ATTACK_TYPE_DAMAGE_MULT[ eType ][ self.atkType ]
        self._hp_dmg_taken += dmg * mult

    def healDamage( self, dmg ):
        self._hp_dmg_taken = max( 0, self._hp_dmg_taken - hp ) # no overheal

    ##### Attacking
    def doAttack( self, enemies ):
        if not self.isAlive: return

        self.atkTTA -= 1
        if self.atkTTA > 0: return

        targ = self.getTarget( enemies )
        if DEBUG_TARGETTING:
            cprint( 'ATTACK: %s -----> %s' % ( self.idname, getattr( targ, 'idname', None ) ), 'white', 'on_blue' )
        if not targ: return

        self.attackTarget( targ )

        self.atkTTA = self.atkCooldown

    def attackTarget( self, targ ):
        targ.takeDamage( self.atk, self.atkType )

    ##### Targetting
    def getTarget( self, enemies ):
        if self.suggestedTarget and self.suggestedTarget.isTargettable:
            return self.suggestedTarget

        # pick target who attacks next; tie breaker goes to whomever is weakest vs our type
        es = [ e for e in enemies if e.isTargettable ]
        es = sorted( es, key=lambda e: e.atkTTA*10 + e.calcDmgMult( self.atkType ) )
        if es: return es[0]

    ##### Rendering
    def showBrief( self ):
        s = '{name} {curHP} | {atk}[{atkType}]{atkTTA}'.format(
            name = self.idname, curHP = self.curHP,
            atk = self.atk, atkType = self.atkType[0], atkTTA = self.atkTTA, )
        return colored( s, 'white' if self.isAlive else 'red' )

    def showDetailed( self ):
        s = '{name} {curHP}/{maxHP} HP | {atk}[{atkType}]{atkTTA} | AS: {answerSkill} SS: {specialSkill}'.format(
            name = self.idname, curHP = self.curHP, maxHP = self.maxHP,
            atk = self.atk, atkType = self.atkType, atkTTA = self.atkTTA,
            answerSkill = self.answerSkill, specialSkill = self.specialSkill, )
        return colored( s, 'white' if self.isAlive else 'red' )

    def __str__( self ): return self.showDetailed().strip()
    def __repr__( self ): return '<<<%s>>>' % self.__str__()

################################################################################
## Driver / Tests
################################################################################
def main():
    b = Battle()
    b.step()
    b.step()
    b.step()
    b.step()

if __name__ == '__main__': main()
