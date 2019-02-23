import sys
import os
from hashlib import sha512
from transaction import VotingClient
DEFAULT_URL = 'http://rest-api:8008'
KEY_NAME = 'votingjar'

def _get_private_keyfile(key_name):
    '''Get the private key for key_name.'''
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")
    return '{}/{}.priv'.format(key_dir, key_name)

def vote_action(party,name):
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = VotingClient(base_url=DEFAULT_URL, key_file=privkeyfile)
    client.vote(party,name)    

def add_action(party):
      privkeyfile = _get_private_keyfile(KEY_NAME)
      client = VotingClient(base_url=DEFAULT_URL, key_file=privkeyfile)
      print('adding party.........'+str(' '.join(party)))
      res=client.add(party)
      print(res)
      

def get_parties(party):
      privkeyfile = _get_private_keyfile(KEY_NAME)
      client = VotingClient(base_url=DEFAULT_URL, key_file=privkeyfile)
      client.list_parties(party)    

def run():
     args=sys.argv
     if len(args)<2: 
          print('....Enter arguments...')
          return
     if args[1]=='vote':
          try: vote_action(args[2],args[3]) 
          except : print('Vote Error')     
     elif args[1]=='add':
          if len(args[2:]) == 0: return
          try: add_action(args[2:])
          except : print('Add error')     
     elif args[1]=='list':
          try:get_parties(args[2])
          except:print('display Error')     
     else: print('.......fuck off.......')          
     
     
if __name__ == "__main__":       
     run()
