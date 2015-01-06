#!/usr/bin/env python
#-*- coding: utf-8 -*-

import json, socket
import win32gui, win32con, re
import time

#ADDR = "192.168.1.19"
ADDR = 'localhost'
PORT = 2112
ANKI_TITLE_PAT = 'Anki -'

def getWindow( titlePat ):
    winlist = []
    toplist = []
    def enum_callback( hwnd, results ):
        winlist.append( ( hwnd, win32gui.GetWindowText( hwnd ) ) )
    win32gui.EnumWindows( enum_callback, toplist )
    wins = [ (hwnd,title) for hwnd, title in winlist if re.search( titlePat, title ) ]
    if len( wins ) != 1:
        raise RuntimeError, 'Found %d matching windows but need exactly 1. Pat="%s". Windows=%s' % ( len(wins), titlePat, wins )
    return wins[0]

def focus( titlePat ):
    win = getWindow( titlePat )
    print 'Focusing "%s"' % win[1]

    #win32gui.SystemParametersInfo( win32con.SPI_SETFOREGROUNDLOCKTIMEOUT, 0, win32con.SPIF_SENDWININICHANGE | win32con.SPIF_UPDATEINIFILE )
    win32gui.ShowWindow( win[0], win32con.SW_SHOWDEFAULT ) # or SW_RESTORE
    #win32gui.UpdateWindow( win[0] )
    win32gui.SetForegroundWindow( win[0] )

    #win32gui.UpdateWindow( win[0] )
    #win32gui.RedrawWindow( win[0], None, None, win32con.RDW_ALLCHILDREN )
    #win32gui.UpdateWindow( win[0] )

def unfocus( titlePat ):
    win = getWindow( titlePat )
    win32gui.ShowWindow( win[0], win32con.SW_MINIMIZE ) #TODO: perhaps just focus this window instead?

def send( data ):
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.connect( ( ADDR, PORT ) )
    s.send( json.dumps( data ) )

    r = s.recv( 1024 ) #TODO: should read more carefully / pre-pend msg length
    s.close()

    return json.loads( r )

def cmd( data ):
    focus( ANKI_TITLE_PAT )
    r = send( data )
    unfocus( ANKI_TITLE_PAT )
    print '%s -----> %s' % ( data, r )

def main():
    '''
    cmd( {'cmd':'echo', 'msg':'Hello World'} ) # should echo msg

    cmd( {'cmd':'get models'} ) # return list of models
    cmd( {'cmd':'get decks'} ) # return list of decks

    cmd( {'cmd':'go study'} ) # should go to overview screen
    cmd( {'cmd':'go study', 'deck':'Sentences'} ) # should go to overview screen of specified deck

    cmd( {'cmd':'go review','deck':'Sentences'} ) # should start review of deck
    '''

    cmd( {'cmd':'go review once'} ) # should do 1 card review then stop and return user feedback

    #TODO: different options for reviewing due cards vs learning new cards
    # query how many due vs new are available

main()
