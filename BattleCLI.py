#-*- coding: utf-8 -*-
import cmd

class BattleCLI( cmd.Cmd ):
    def __init__( self, battle, *args, **kwargs ):
        self.battle = battle
        cmd.Cmd.__init__( self, *args, **kwargs )

    def preloop( self ):
        print self.battle.show()

    def do_show( self, line ):
        '''Displays the current battle status'''
        print self.battle.show()

    def do_choose( self, optStr ):
        '''Choose a test option by providing it's number
        Ex: choose 3
        '''
        try:
            optNum = int( optStr )
            opt = self.battle.testOptions[ optNum ]
            self.battle.testOptions[ optNum ] = None

            print 'Choosing option', opt
            self.chosenOption = opt # the return isn't threaded through to cmdloop's return, which makes this ugly
            return True
        except (KeyError,ValueError):
            print 'Invalid option number', optStr

    def do_special( self, cidStr ):
        '''Use special of the given creature id number
        Ex: `special 3` activates the special skill of the 4th creature
        '''
        try:
            cid = int( cidStr )
            c = [ a for a in self.battle.allies + self.battle.enemies if a.id == cid ][0]

            if c not in self.battle.allies:
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
            c.specialSkill.onActivate()

        except (ValueError,IndexError):
            print 'Invalid creature id', cidStr
