#!/usr/bin/env python3
#GNU General Public License v3.0
#Code by MegaKG

def typeHeader(Options,PassIN):
    return 'text/html; charset=UTF-8'

def headerExtra(Options,PassIN):
    return ''

def body(Options,CON,PassIN):
    return b'<!DOCTYPE html><html>Hello World</html>'

def websocket(Options,CON,PassIN):
    CON.close()