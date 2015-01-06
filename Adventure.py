#-*- coding: utf-8 -*-
from   Battle import Battle
from   Config import TEST_TYPE
from   Utils  import cprint

class Adventure:
    '''Represents a series of battles with persisted creature state'''
    def __init__( self, party ):
        self.testType = TEST_TYPE
        self.party = party
        self.encounterNumber = 0
        self.preAdventure()

    def run( self ):
        '''Execute adventure to completion. Returns whether succeeded or not'''
        for e in self.getNextEncounter():
            cprint( 'Begining new battle', 'green' )
            self.encounterNumber += 1
            b = Battle( self.party, e, self.testType, self.encounterNumber )
            b.run()

            if b.isLost:
                cprint( 'After %d battles, you have failed the adventure' % self.encounterNumber, 'red' )
                return False

        cprint( 'After %d battles, you have won the adventure!' % self.encounterNumber, 'green' )
        self.postAdventure()
        return True

    # these are meant to be overridden
    def preAdventure( self ): pass
    def postAdventure( self ): pass
    def getNextEncounter( self ):
        '''Generator that yields a list of enemies for the next encounter.
        Adventure ends when generator does'''
        yield
