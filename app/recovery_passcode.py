from datetime import datetime, timedelta
import string
import secrets

def passcode_generation():
    charSelection = string.ascii_letters + string.digits
    passcode = ''
    for i in range(10):
        passcode += ''.join(secrets.choice(charSelection))
    return passcode

def passcode_check(passcode, code):
    return code == passcode




