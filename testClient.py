#!/usr/bin/env python
#-*- coding: utf-8 -*-

import json, socket

ADDR = "192.168.1.19"
PORT = 2112

def send( data ):
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.connect( ( ADDR, PORT ) )
    s.send( json.dumps( data ) )

    r = s.recv( 1024 ) #TODO: should read more carefully / pre-pend msg length
    s.close()

    return json.loads( r )

def cmd( data ):
    r = send( data )
    print '%s -----> %s' % ( data, r )

def main():
    '''
    cmd( {'cmd':'echo', 'msg':'Hello World'} ) # should echo msg

    cmd( {'cmd':'get models'} ) # return list of models
    cmd( {'cmd':'get decks'} ) # return list of decks

    cmd( {'cmd':'go study'} ) # should go to overview screen
    cmd( {'cmd':'go study', 'deck':'Sentences'} ) # should go to overview screen of specified deck

    cmd( {'cmd':'review','deck':'Sentences'} ) # should start review of deck
    '''

    cmd( {'cmd':'review once'} ) # should do 1 card review then stop and return user feedback

    #TODO: different options for reviewing due cards vs learning new cards
    # query how many due vs new are available

main()
