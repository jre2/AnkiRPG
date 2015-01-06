#!/usr/bin/env python
#-*- coding: utf-8 -*-

#import colorama; colorama.init() # this makes termcolor work on windows
import itertools
from operator import mul
from termcolor import colored, cprint

'''TODO
* REPL with player targetting, SS activation, and category selection
* External interaction with Anki (show review, get feedback)
* Extend Battle to get config from adventure
  - start with a simple trash encounter + boss fight style adventures, refactoring Battle as needed
* Collection, creature progression (levels/evolutions), and deck mangement
'''


################################################################################
## Debug
################################################################################
DEBUG_TARGETTING = True
def debug( txt ): print colored( txt, 'white', 'on_blue' )

################################################################################
## Hofs
################################################################################
def product( xs ): return reduce( mul, xs, 1 )

################################################################################
## Skills and Buffs
################################################################################
class Buffs:
    '''Accessing buffs.foo provides a list of all .foo that exist in any buff'''
    def __init__( self ):
        self._buffs = []

    def __getattr__( self, name ): return [ getattr( b, name ) for b in self._buffs if getattr( b, name ) ]

    def _append( self, b ): self._buffs.append( b )

    def _update( self ):
        for b in self._buffs: b.update()
        self._buffs = [ b for b in self._buffs if b.isValid ]

    def __str__( self ): return self._buffs.__str__()

class Buff:
    '''Represents a number of stats modifiers (default to None if not defined)
    that aren't applied once a buff runs out (TTL<1) or the owner causing the
    buff is no longer alive. TTL=None implies infinite duration
    Ex:
    > b = Buff( dmgFlat=100 )
    > b.dmgFlat
    100
    > b.dmgMult
    None
    '''
    def __init__( self, owner, ttl=None, **kwargs ):
        self._owner = owner
        if 'ttl' in kwargs:
            ttl = kwargs.pop('ttl')
        self._TTL = ttl
        self._kwargs = kwargs

    def __getattr__( self, name ): return self._kwargs[ name ] if name in self._kwargs and self.isValid else None

    @property
    def isValid( self ): return self._owner.wasAlive and (self._TTL is None or self._TTL > 0)

    def update( self ):
        if self._TTL is not None:
            self._TTL -= 1

    def __str__( self ):  return '<Buff:TTL:%s:%s>' % ( self._TTL, self._kwargs )
    def __repr__( self ): return self.__str__()

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
        from copy import deepcopy
        s = deepcopy( self )
        s.me = owner
        return s

    def update( self, correct, asProced, acting ):
        if acting and correct and asProced:
            self._numASproced += 1
            self._numASprocedInARow += 1

        if not correct:
            self._numASprocedInARow -= 1

    def __str__( self ):
        return '<%s:%s>' % (self.__class__.__name__, self.kwargs)

    # this hook runs before attack phase iff proced
    def onAnswer( self ): pass
    # this hook runs as attack happens iff proced
    def onAttack( self, targ ): pass

    # this is checked during user REPL; no side-effects allowed
    def canActivate( self ): return False
    # this hook runs when user requests
    def onActivate( self ): pass

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
        self._numASproced = 0

        dmg = self.me.atk * self.nukeMult
        es = [ e for e in self.me.enemies if e.isTargettable ]
        for e in es:
            e.takeDamage( dmg, self.me.atkType )

class PassiveBuffSelf( Skill ): # BuffParams
    def onPassive( self ):
        self.me.addBuff( self.me, self.kwargs )

class PassiveBuffSameType( Skill ): # BuffParams
    def onPassive( self ):
        for a in self.me.allies:
            if a.atkType == self.me.atkType and a.isAlive:
                a.addBuff( self.me, self.kwargs )

################################################################################
## Creature DB
################################################################################
CREATURE_DB = {
    'Alice':    ( 500, 250, 'Fire', 1, BuffSameType( dmgFlat=100, ttl=2 ), NukeSingle( nukeMult=1.15, N=2 ) ),
    'Bob':      ( 450, 300, 'Lightning', 2, BuffSameType( dmgFlat=50, dmgMult=1.1 ), NukeSingle( nukeMult=1.25, N=7 ), [PassiveBuffSelf( hpFlat=110 )] ),
    'Charlie':  ( 550, 200, 'Water', 2, BuffSelf( dmgMult=1.2 ), NukeSingle( nukeMult=1.50, N=3 ) ),
    'Boss':     ( 2000, 200, 'Fire', 3, UndividedAOE( aoeMult=1.0 ) ),
    'David':    ( 1000, 100, 'Water', 1, BuffSelfAfterN( dmgFlat=100, N=1 ) ),
    }

################################################################################
## Battle board
################################################################################
class Battle:
    def __init__( self ):
        self.numRounds = 0
        self.testOptions = {1:None, 2:None, 3:None, 4:None }
        #self.testType = 'NoTest'
        self.testType = 'Anki'

        self.allies  = self.mkCreatures([ 'Alice', 'Alice', 'Bob', 'Charlie' ], cds= self.testType == 'NoTest' )
        self.enemies = self.mkCreatures([ 'Alice', 'Boss', 'Charlie', 'David' ], cds= True )

        self.onBattleStart()

    def show( self ):
        banner = ( ' Round %d ' % self.numRounds ).center( 80, '#' )
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

    def mkCreature( self, name, cds ):   return Creature( name, *CREATURE_DB[ name ], useCooldowns=cds )
    def mkCreatures( self, names, cds ): return [ self.mkCreature( name, cds ) for name in names ]

    def refillTestOptions( self ):
        for k,v in self.testOptions.items():
            if not v:
                self.testOptions[k] = self.mkTestOption()

    def mkTestOption( self ):
        def weightedChoice( cws ): # [(Choice,Weight)] -> Rand Choice
            from random import random
            from bisect import bisect

            values, weights = zip(*cws)
            total = 0
            cum_weights = []
            for w in weights:
                total += w
                cum_weights.append(total)
            x = random() * total
            i = bisect(cum_weights, x)
            return values[i]

        c = weightedChoice( [ ('Fire',25), ('Water',25), ('Lightning',25), ('Fire/Water',7), ('Fire/Lightning',7), ('Water/Lightning',7), ('Fire/Water/Lightning',4) ] )
        return c

    def onBattleStart( self ):
        self.applyPassives()

    def applyPassives( self ):
        for c in self.allies + self.enemies:
            c.doPassives()

    def step( self ):
        '''
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
        self.refillTestOptions()

        # 3-5. TODO: CLI repl to handle user target suggestion and SS activation until category selection
        print self.show()

            # choosen random category
        from random import randint
        n = randint( 1, 4 )

        chosenOption = self.testOptions[ n ]
        self.testOptions[ n ] = None
        debug( 'OPTION: %s' % chosenOption )

            # activate specials randomly
        for c in self.allies:
            if c.isAlive and c.specialSkill and c.specialSkill.canActivate():
                c.specialSkill.onActivate()
                debug( 'ACTIVATE: %s' % c.idname )

        # 6. user-test
        testPassed = True
        testProcedAnswerSkill = True
        #TODO: launch/control external Anki instance to review a card and get feedback
            # modify the above if applicable
        if self.testType == 'Anki':
            pass

        # 7. resolve combat
            # figure out which creatures get to act
        actingAllies = [ c for c in self.allies if c.canAttack and c.atkType in chosenOption ]
        actingEnemies = [ c for c in self.enemies if c.canAttack ]
        acting = actingAllies + actingEnemies

            # update creatures with test results (eg. for skill charges)
        for c in self.allies:   c.testUpdate( testPassed, testProcedAnswerSkill, c in acting )
        for c in self.enemies:  c.testUpdate( True, True, c in acting )

            # for those that get to, proc onAnswer and then attack with them
        for c in actingAllies:  c.onAnswer()
        for c in actingAllies:  c.doAttack( testProcedAnswerSkill )

            # if enemy could use specials, they'd use them now
        for c in actingEnemies: c.onAnswer()
        for c in actingEnemies: c.doAttack( True )

        # 8. post-round book keeping
        self.numRounds += 1

################################################################################
## Creature
################################################################################
class Creature:
    ATTACK_TYPE_DAMAGE_MULT = {
            'Fire':         { 'Fire':1.0, 'Water':0.5, 'Lightning':1.5, },
            'Water':        { 'Fire':1.5, 'Water':1.0, 'Lightning':0.5, },
            'Lightning':    { 'Fire':0.5, 'Water':1.5, 'Lightning':1.0, },
            }
    NEXT_ID = itertools.count(0)

    def __init__( self, name, hp, atk, atkType, atkCooldown, answerSkill=None, specialSkill=None, passives=None, useCooldowns=True ):
        self.name = name
        self.id = Creature.NEXT_ID.next()
        self.idname = '%d %10s' % ( self.id, '[%s]' % self.name )

        self._maxHP = hp
        self._curHP = hp
        self._hp_dmg_taken = 0
        self.wasAlive = True # whether we were alive last round; mostly used to see when buffs die out

        self._atk = atk
        self.atkType = atkType
        if not useCooldowns: atkCooldown = 0 # disable cooldown mechanism if directed
        self.atkCooldown = atkCooldown
        self.atkTTA      = atkCooldown # Turns Til next Attack

        self._allies = []
        self._enemies = []
        self.suggestedTarget = None

        self.answerSkill = answerSkill.new( self ) if answerSkill else None
        self.specialSkill = specialSkill.new( self ) if specialSkill else None
        self._numAnsweredCorrectly = 0
        self._numAnsweredCorrectlyInARow = 0
        self._numASproced = 0
        self._numASprocedInARow = 0

        self._passives = [ p.new( self ) for p in passives ] if passives is not None else []

        self.buffs = Buffs()


    def preRoundUpdate( self, allies, enemies ):
        '''Update list of ally and enemy creatures, reduce atk cooldowns, and update buffs'''
        self.wasAlive = self.isAlive

        self.atkTTA = max( 0, self.atkTTA - 1 )

        self._allies = allies
        self._enemies = enemies

        self.buffs._update()

    def testUpdate( self, correct, asProced, acting ):
        '''Track answer totals and streaks so skills can charge abilities based on those'''
        if self.answerSkill:    self.answerSkill.update( correct, asProced, acting )
        if self.specialSkill:   self.specialSkill.update( correct, asProced, acting )

        if acting and correct:
            self._numAnsweredCorrectly += 1
            self._numAnsweredCorrectlyInARow += 1
        if acting and correct and asProced:
            self._numASproced += 1
            self._numASprocedInARow += 1
        if not correct:
            self._numAnsweredCorrectlyInARow = 0
            self._numASprocedInARow = 0

    def addBuff( self, owner, buffParams ):
        self.buffs._append( Buff( owner, **buffParams ) )

    def doPassives( self ):
        for p in self._passives: p.onPassive()

    ##### Stats
    @property
    def atk( self ):
        flat = self._atk + sum( self.buffs.dmgFlat )
        mult = product( self.buffs.dmgMult )
        return flat * mult
    @property
    def maxHP( self ):
        flat = self._maxHP + sum( self.buffs.hpFlat )
        mult = product( self.buffs.hpMult )
        return flat * mult
    @property
    def curHP( self ):  return self.maxHP - self._hp_dmg_taken

    ##### IFF
    @property
    def allies( self ):     return self._allies
    @property
    def enemies( self ):    return self._enemies

    ##### State
    @property
    def isAlive( self ):        return self.curHP > 0
    @property
    def isTargettable( self ):  return self.isAlive
    @property
    def canAttack( self ):      return self.isAlive and self.atkTTA <= 0

    ##### Damage and healing

        # receiver handles dmg (in case their skills modify things), but attack can use this to help
    def calcDmgMult( self, eType ): return Creature.ATTACK_TYPE_DAMAGE_MULT[ self.atkType ][ eType ]
    def calcDmg( self, eType ):     return self.atk * self.calcDmgMult( eType )

    def takeDamage( self, dmg, eType ):
        mult = Creature.ATTACK_TYPE_DAMAGE_MULT[ eType ][ self.atkType ]
        self._hp_dmg_taken += dmg * mult

    def healDamage( self, dmg ):
        self._hp_dmg_taken = max( 0, self._hp_dmg_taken - hp ) # no overheal

    ##### Attacking
    def onAnswer( self ):
        self.answerSkill.onAnswer()

    def doAttack( self, procAS ):
        if not self.canAttack: return

        targ = self.getTarget()
        if DEBUG_TARGETTING:
            debug( 'ATTACK: %s -----> %s' % ( self.idname, getattr( targ, 'idname', None ) ) )
        if not targ: return

        self.attackTarget( targ, procAS )

        self.atkTTA = self.atkCooldown

    def attackTarget( self, targ, procAS ):
        '''Run answer skill's onAttack if it was proced,
        then applies damage to target like normal unless requested not to'''
        if procAS and self.answerSkill:
            r = self.answerSkill.onAttack( targ )
            if r == 'dont run default': return

        targ.takeDamage( self.atk, self.atkType )

    ##### Targetting
    def getTarget( self ):
        if self.suggestedTarget and self.suggestedTarget.isTargettable:
            return self.suggestedTarget

        # pick target who attacks next; tie breaker goes to whomever is weakest vs our type
        es = [ e for e in self.enemies if e.isTargettable ]
        es = sorted( es, key=lambda e: e.atkTTA*10 + e.calcDmgMult( self.atkType ) )
        if es: return es[0]

    ##### Rendering
    def typeColored( self, txt ):
        d = { 'Fire':'red', 'Water':'blue', 'Ligtning':'yellow' }
        return colored( txt, d[ self.atkType ] )

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
        s += ' || Buffs: %s' % self.buffs
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
    b.step()
    b.step()

if __name__ == '__main__': main()
