#-*- coding: utf-8 -*-
from   Config import ANKI_ADDR, ANKI_PORT
from   Utils import  colored, debug, weightedChoice
import json, socket, time

class Test: # virtual
    def __init__( self ):
        self._options = { 1:None, 2:None, 3:None, 4:None }

    def show( self ):
        return colored( ' '.join( '%d %s' % (i,c) for i,(c,_) in self.testOptions.iteritems() ), 'cyan' )

    @property
    def testOptions( self ):
        '''Non-empty mapping of test option id to colors and test category
        :: Map Int ( Colors, Category )'''
        for k,v in self._options.items():
            if v is None:
                color = self._mkColor()
                cat   = self._mkCategory( color )
                self._options[ k ] = ( color, cat )
        return self._options

    def _chooseOption( self, n ):
        '''Choose option n. This removes it and will cause a new option to be
        generated in its place'''
        v = self.testOptions[ n ]
        self.testOptions[ n ] = None
        return v

    def _mkColor( self ): return weightedChoice( [ ('Fire',25), ('Water',25), ('Lightning',25), ('Fire/Water',7), ('Fire/Lightning',7), ('Water/Lightning',7), ('Fire/Water/Lightning',4) ] )

    def doTest( self, optNum ):
        '''Given chosen option, perform test and return (color, if passed, if should proc AS)'''
        color, cat = self._chooseOption( optNum )
        passed, proced = self._doTest( color, cat )
        return ( color, passed, proced )

    # These should be overridden
    def useCooldowns( self ):        return False
    def _mkCategory( self, color ):  return 'UnnamedCategory'
    def _doTest( self, color, cat ): return ( False, False )

class CooldownTest( Test ):
    def useCooldowns( self ):        return True
    def doTest( self, optNum ):      return ( 'Fire/Water/Lightning', True, True )

class NoTest( Test ):
    def _doTest( self, color, cat ): return ( True, True )

class AnkiTest( Test ):
    def send( self, data ):
        self.sock = s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        s.connect( ( ANKI_ADDR, ANKI_PORT ) )
        s.sendall( json.dumps( data ) )

    def recv( self ):
        r = self.sock.recv( 4096 ) #TODO: fetch entire msg in robust fashion
        return json.loads( r )

    def cmd( self, data ):
        self.send( data )
        r = self.recv()
        self.sock.close()
        return r

    #TODO: categories based on decks and/or models
    def _mkCategory( self, color ): return 'UnnamedCategory'

    def _doTest( self, color, cat ):
        r = self.cmd( {'cmd':'go review once'} )

        if r['ease'] > 1: return ( True, True )
        else:             return ( False, False )
