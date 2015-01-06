#-*- coding: utf-8 -*-
class Buffs:
    '''Accessing buffs.foo provides a list of all .foo that exist in any buff
    Container manipulation functions are prefixed by underscore but don't imply private
    '''
    def __init__( self ):
        self._buffs = []

    def __getattr__( self, name ): return [ getattr( b, name ) for b in self._buffs if getattr( b, name ) ]

    def _append( self, b ): self._buffs.append( b )

    def _update( self ):
        for b in self._buffs: b.update()
        self._buffs = [ b for b in self._buffs if b.isValid ]
    def _clear( self ):
        self._buffs = []

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
