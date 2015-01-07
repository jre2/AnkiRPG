# -*- coding: utf-8 -*-
import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
import PyQt4.QtNetwork as QtNetwork

import json, os

from aqt import mw
from anki.hooks import addHook, wrap
from aqt.reviewer import Reviewer
from aqt.utils import showCritical, showInfo, showWarning

def takeFocus():
    '''This works if Anki was minimized or if the foreground window gives us permission.
    Ie. it doesn't work if we're non-minimized and simply lost focus'''
    mw.setWindowState( mw.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive )
    mw.activateWindow()
    #mw.app.setActiveWindow( mw )
    #mw.app.activeWindow().setFocus()

def passFocus():
    '''Pass focus back to client by minimizing ourself'''
    mw.showMinimized()

class AnkiServer( object ):
    def __init__( self, port=2112 ):
        self.logFile = open( os.path.join( mw.pm.profileFolder(), 'AnkiRPGServer.log' ), 'w' )
        self.server = QtNetwork.QTcpServer()
        self.server.listen( address=QtNetwork.QHostAddress.Any, port=port )
        QtCore.QObject.connect( self.server, QtCore.SIGNAL( 'newConnection()' ), self.onNewConnection )

        self.notifyCardAnswer = False

    def log( self, txt ): self.logFile.write( str(txt) +'\n' )

    def onNewConnection( self ):
        self.sock = self.server.nextPendingConnection() # we only handle 1 connection at a time
        QtCore.QObject.connect( self.sock, QtCore.SIGNAL( 'readyRead()' ), self.onReadyRead )

    def onReadyRead( self ):
        data = json.loads( str( self.sock.readAll() ) )
        self.log( data )

        # run cmd then reply with result unless it's None
        fname = 'cmd_' + data['cmd'].replace(' ','_')
        if hasattr( self, fname ):
            r = getattr( self, fname )( data )
            if r is not None:
                self.reply( r )
        else:
            self.reply( {'error':'Invalid command', 'fname':fname} )

    def reply( self, data ): self.sock.write( QtCore.QByteArray( json.dumps( data ) ) )

    def shutdown( self ):
        self.logFile.close()

    ##### Commands

    def cmd_echo( self, data ): return data['msg']
    def cmd_get_models( self, data ): return mw.col.models.allNames()
    def cmd_get_decks( self, data ): return mw.col.decks.allNames()

    def cmd_go_study( self, data ):
        takeFocus()
        if 'deck' in data: mw.col.decks.select( mw.col.decks.id( data['deck'] ) )
        mw.onOverview()
        return "OK"

    def cmd_go_review( self, data ):
        takeFocus()
        if 'deck' in data: mw.col.decks.select( mw.col.decks.id( data['deck'] ) )
        mw.col.startTimebox()
        mw.moveToState( 'review' )
        return "OK"

    def cmd_go_review_once( self, data ):
        takeFocus()
        if 'deck' in data: mw.col.decks.select( mw.col.decks.id( data['deck'] ) )
        mw.col.startTimebox()
        mw.moveToState( 'review' )

        # instead of replying ourself, set flag so onCardAnswer hook will reply
        #   this also lets user back out and do other things, then reply after they finally answer
        self.notifyCardAnswer = True

def onCardAnswer( self, ease, _old=None ):
    if not mw.server.notifyCardAnswer: return _old( self, ease )

    # reimplementation of _answerCard, but instead of getting next card, go to overview screen
    if self.mw.state != "review": return
    if self.state != "answer": return
    if self.mw.col.sched.answerButtons( self.card ) < ease: return
    self.mw.col.sched.answerCard( self.card, ease )
    self._answeredIds.append( self.card.id )
    self.mw.autosave()
    #self.nextCard()
    mw.onOverview()

    # send notice to client
    mw.server.reply( {'card':self.card.id, 'ease':ease} )
    mw.server.notifyCardAnswer = False
    passFocus()

def startServer():
    mw.server = AnkiServer()

addHook( 'profileLoaded', startServer )
Reviewer._answerCard = wrap(Reviewer._answerCard, onCardAnswer, "around")
