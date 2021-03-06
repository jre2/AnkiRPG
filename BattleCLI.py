#-*- coding: utf-8 -*-
import cmd
from   Utils import debug
#IDEA: clear screen between rounds ?

class BattleCLI( cmd.Cmd ):
    def __init__( self, player, battle, *args, **kwargs ):
        self.player = player
        self.battle = battle
        cmd.Cmd.__init__( self, *args, **kwargs )

    def preloop( self ):
        print self.battle.show( self.player )
        print self.player.playerTest.show()

    def do_show( self, line ):
        '''Displays the current battle status'''
        print self.battle.show( self.player )
        print self.player.playerTest.show()

    def do_choose( self, optStr ):
        '''Choose a test option by providing it's number
        Ex: choose 3
        '''
        try:
            optNum = int( optStr )
            color = self.player.playerTest.testOptions[ optNum ][0]

            # the return isn't threaded through to cmdloop's return, so store on attr
            print 'Choosing option %d: %s' % ( optNum, color )
            self.chosenTestOption = optNum
            return True
        except (KeyError,ValueError):
            print 'Invalid option number', optStr

    def do_special( self, cidStr ):
        '''Use special of the given creature id number
        Ex: `special 3` activates the special skill of the 4th creature
        '''
        try:
            cid = int( cidStr )
            c = self.battle.creatureById( cid )

            if c not in self.player.party:
                print "That creature doesn't belong to you"
                return
            if not c.isAlive:
                print "That creature isn't alive"
                return
            if not c.specialSkill:
                print "That creature doesn't have a special skill"
                return
            if not c.specialSkill.canActivate():
                print "That creature's special isn't ready"
                return

            debug( 'ACTIVATE: %s' % c.idname )
            r = c.specialSkill.onActivate()
            if r == False:
                print 'The skill has no effect'

        except (ValueError,IndexError):
            print 'Invalid creature id', cidStr
