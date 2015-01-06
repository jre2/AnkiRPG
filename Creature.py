#-*- coding: utf-8 -*-
import itertools
from   Config import DEBUG_TARGETTING
from   Buff   import Buffs, Buff
from   Utils  import colored, debug, product

class Creature:
    ATTACK_TYPE_DAMAGE_MULT = {
            'Fire':         { 'Fire':1.0, 'Water':0.5, 'Lightning':1.5, },
            'Water':        { 'Fire':1.5, 'Water':1.0, 'Lightning':0.5, },
            'Lightning':    { 'Fire':0.5, 'Water':1.5, 'Lightning':1.0, },
            }
    NEXT_ID = itertools.count(0)

    def __init__( self, name, hp, atk, atkType, atkCooldown, answerSkill=None, specialSkill=None, passives=None, useCooldowns=True ):
        self.name   = name
        self.id     = Creature.NEXT_ID.next()
        self.idname = '%d %10s' % ( self.id, '[%s]' % self.name )

        self._maxHP = hp
        self._curHP = hp

        self._atk        = atk
        self.atkType     = atkType
        self.atkCooldown = atkCooldown if useCooldowns else 0

        # these instances are not specific to this creature but will be replaced later
        self.answerSkill  = answerSkill
        self.specialSkill = specialSkill
        self._passives    = passives

        self.fullReset()

    def fullReset( self ):
        '''Clear all buffs, reset atk cooldown, reset target, remove dmg, reset skills'''
        self.preBattleInit()

        self._hp_dmg_taken = 0
        self.wasAlive      = True # whether was alive last round; used for buff upkeep

        self.answerSkill  = self.answerSkill.new( self ) if self.answerSkill else None
        self.specialSkill = self.specialSkill.new( self ) if self.specialSkill else None
        self._passives    = [ p.new( self ) for p in self._passives ] if self._passives else []

        self._numAnsweredCorrectly       = 0
        self._numAnsweredCorrectlyInARow = 0
        self._numASproced                = 0
        self._numASprocedInARow          = 0

    def preBattleInit( self ):
        '''Clear all buffs, reset atk cooldown, reset target'''
        self.buffs  = Buffs()
        self.atkTTA = self.atkCooldown # turns til next attack

        self._allies         = []
        self._enemies        = []
        self.suggestedTarget = None

    def preRoundUpdate( self, allies, enemies ):
        '''Update list of ally and enemy creatures, reduce atk cooldowns, and update buffs'''
        self.wasAlive = self.isAlive

        self.atkTTA = max( 0, self.atkTTA - 1 )

        self._allies  = allies
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
        '''Creature gains buff specified by buffParams. It is lost if owner dies'''
        self.buffs._append( Buff( owner, **buffParams ) )

    def doPassives( self ):
        '''Trigger all passive skills'''
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
        '''Take dmg of the specified type. Type advantage is factored'''
        mult = Creature.ATTACK_TYPE_DAMAGE_MULT[ eType ][ self.atkType ]
        self._hp_dmg_taken += dmg * mult

    def healDamage( self, dmg ):
        '''Heal the specified amount of dmg. No overhealing.'''
        self._hp_dmg_taken = max( 0, self._hp_dmg_taken - hp )

    ##### Attacking
    def onAnswer( self ):
        '''Trigger onAnswer portion of Answer Skill'''
        self.answerSkill.onAnswer()

    def doAttack( self, procAS ):
        '''Perform an attack if off cooldown and a valid target exists.
        If procAS, attack will trigger onAttack portion of Answer Skill'''
        if not self.canAttack: return

        targ = self.getTarget()
        if DEBUG_TARGETTING:
            debug( 'ATTACK: %s -----> %s' % ( self.idname, getattr( targ, 'idname', None ) ) )
        if not targ: return

        self.attackTarget( targ, procAS )

        self.atkTTA = self.atkCooldown

    def attackTarget( self, targ, procAS ):
        '''Run answer skill's onAttack if it was proced, then apply dmg to
        target like normal unless requested not to'''
        if procAS and self.answerSkill:
            r = self.answerSkill.onAttack( targ )
            if r == 'dont run default': return

        targ.takeDamage( self.atk, self.atkType )

    ##### Targetting
    def getTarget( self ):
        '''Return best target to attack, if there is one.
        If player has set a target, use that if possible.'''
        if self.suggestedTarget and self.suggestedTarget.isTargettable:
            return self.suggestedTarget

        # pick target who attacks next; tie breaker goes to whomever is weakest vs our type
        es = [ e for e in self.enemies if e.isTargettable ]
        es = sorted( es, key=lambda e: e.atkTTA*10 + e.calcDmgMult( self.atkType ) )
        if es: return es[0]

    ##### Rendering
    def showBrief( self ):
        '''Render basic stats to string'''
        s = '{name} {curHP} | {atk}[{atkType}]{atkTTA}'.format(
            name = self.idname, curHP = self.curHP,
            atk = self.atk, atkType = self.atkType[0], atkTTA = self.atkTTA, )
        return colored( s, 'white' if self.isAlive else 'red' )

    def showDetailed( self ):
        '''Render detailed stats to string'''
        s = '{name} {curHP}/{maxHP} HP | {atk}[{atkType}]{atkTTA} | AS: {answerSkill} SS: {specialSkill}'.format(
            name = self.idname, curHP = self.curHP, maxHP = self.maxHP,
            atk = self.atk, atkType = self.atkType, atkTTA = self.atkTTA,
            answerSkill = self.answerSkill, specialSkill = self.specialSkill, )
        s += ' || Buffs: %s' % self.buffs
        return colored( s, 'white' if self.isAlive else 'red' )

    def __str__( self ): return self.showDetailed().strip()
    def __repr__( self ): return '<<<%s>>>' % self.__str__()
