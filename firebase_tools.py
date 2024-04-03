import os
import json 
import firebase_admin 
from firebase_admin import db

FIREBASE_URL=os.getenv("FIREBASE_URL")

FIREBASE_KEY=os.getenv("FIREBASE_KEY")
FIREBASE_KEY=json.loads(FIREBASE_KEY.replace("'","\"")) 


cred = firebase_admin.credentials.Certificate(FIREBASE_KEY)
firebase_admin.initialize_app(cred, {'databaseURL':FIREBASE_URL})


##=====================================================================||====##
##=====================================================================||====##
def ReferenceGet(path) : 
  reference = db.reference(path)
  #print( reference )
  if reference.get() is None : 
    print("[ReferenceGet] reference is None")
    return None 
  else : 
    return reference


def ReferenceKeysPrint(path) :
  for key in ReferenceGet(path).get():
    print("[ReferenceKeysPrint] db('%s')->'%s'" %(path,key))


##=====================================================================||====##
##=====================================================================||====##
###ReferenceKeysPrint("/")

Guests = ReferenceGet("/Guests")
Calls = ReferenceGet("/Guests/Calls")
Threads = ReferenceGet("/Guests/Threads")

ReferenceKeysPrint("/Guests")
##assert not ReferenceGet("/Guests").child('Threads').get()

##=====================================================================||====##
##=====================================================================||====##
