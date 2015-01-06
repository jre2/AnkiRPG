#-*- coding: utf-8 -*-
from   Creature import Creature
from   Skills import *

CREATURE_DB = {
    'Alice':    ( 500, 250, 'Fire', 1, BuffSameType( dmgFlat=100, ttl=2 ), NukeSingle( nukeMult=1.15, N=2 ) ),
    'Bob':      ( 450, 300, 'Lightning', 2, BuffSameType( dmgFlat=50, dmgMult=1.1 ), NukeSingle( nukeMult=1.25, N=7 ), [PassiveBuffSelf( hpFlat=110 )] ),
    'Casey':    ( 550, 50, 'Water', 2, BuffSelf( dmgMult=1.2 ), MagicMissile( nukeMult=1.50, N=1 ) ),
    'Charlie':  ( 550, 200, 'Water', 2, BuffSelf( dmgMult=1.2 ), MagicMissile( nukeMult=1.50, N=3 ) ),
    'Boss':     ( 2000, 200, 'Fire', 3, UndividedAOE( aoeMult=1.0 ) ),
    'David':    ( 1000, 100, 'Water', 1, BuffSelfAfterN( dmgFlat=100, N=1 ) ),
    'The Darkness': ( 1000, 50, 'Lightning', 5, BuffSelf( hpFlat=50 ), NukeSingle( nukeMult=1.10, N=5 ) ),
    }

def mkCreature( name, cds ):   return Creature( name, *CREATURE_DB[ name ], useCooldowns=cds )
def mkCreatures( names, cds ): return [ mkCreature( name, cds ) for name in names ]
