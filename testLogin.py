#!/usr/bin/env python3
import time
#import UNIXstreams3


#Yes, this is insecure... you do realise that this is a test right?
Users = {
    'test':'testpwd'
}


Tokens = []

LoginForm = """
<!DOCTYPE html>
<html>
<form action='login' method='post'>
<input type='hidden' name='action' value='login'>
Username: <input type='text' name='username'>
Password: <input type='password' name='password'>
<input type='submit' value='Login!'>
</form>

</html>
"""

LoggedIn = """
<!DOCTYPE html>
<html>
<h1>Logged In!</h1>
<form action='login' method='post'>
<input type='hidden' name='action' value='logout'>
<input type='submit' value='Logout!'>
</form>
</html>
"""

def auth(User,PWD):
    global Tokens
    if User in Users:
        if PWD == Users[User]:
            T = str(time.time())
            Tokens.append(T)
            print("User Allowed!")
            return T
    print("User Denied")
    return ''

def checktok(Tok):
    print("Check Token")
    return Tok in Tokens
        

def loadCookie(CV):
    print("Get Cookies")
    C = CV.split('; ')
    OUT = {}
    for i in C:
        SP = i.split('=')
        OUT[SP[0]] = SP[1]
    return OUT

def setCookie(N,V):
    print("Set Cookie")
    return "Set-Cookie: " + N + '=' + V + '; SameSite=Strict; Secure; HttpOnly'


def typeHeader(Options,PassIn):
    return 'text/html; charset=UTF-8'

def headerExtra(Options,PassIn):
    INITIAL = "Content-Security-Policy: default-src 'self'; object-src 'none'"
    if 'action' in Options:
        if Options['action'] == 'login':
            print("Action Login")
            #Check
            TOK = auth(Options['username'],Options['password'])
            if TOK == '':
                pass
            else:
                return INITIAL + '\n' + setCookie("Token",TOK)
        elif Options['action'] == 'logout':
            print("Action Logout")
            return INITIAL + '\n' + setCookie("Token",'')
    return INITIAL

def body(Options,CON,PassIn):
    if 'Cookie' in Options:
        COOK = loadCookie(Options['Cookie'])
    else:
        COOK = {}

    if 'Token' in COOK:
        if checktok(COOK['Token']):
            return LoggedIn.encode()
    
    return LoginForm.encode()


    
