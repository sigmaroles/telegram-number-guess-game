from flask import Flask, request
from cloudant import Cloudant
import cf_deployment_tracker
import requests
import os
import random
import json
import atexit

MAX_NUM = 100
# due to bad design, the actual attempts is MAX_ATT+1. don't even ask..
MAX_ATT = 5

class Game:
    def __init__(self, uid):
        self.uid = uid
        self.attempts = MAX_ATT - 1
        self.guesses = []
        self.num = random.randint(1, MAX_NUM-1)
        self.status = "live"
    
    def isLive(self):
        return self.status=='live'
        
    def play_turn(self, guess):
        if self.status != 'live':
            return self.status
        else:
            self.guesses.append(guess)
            if self.attempts <= 0:
                self.status = "lost"
                return self.status
            self.attempts-= 1
            if self.num == guess:
                self.status = "won"
                return "won"
            elif self.num < guess:
                return "go lower"
            else: 
                return "go higher"
                

app = Flask(__name__)
with open('bottoken.txt', 'r') as ft:
    bottoken = ft.read().strip()
sendURL = 'https://api.telegram.org/bot' + bottoken + "/sendMessage"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
activeGames = {}


# --- IBM cloud config stuff starts

cf_deployment_tracker.track()
db_name = 'mydb'
client = None
db = None

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)

@atexit.register
def shutdown():
    if client:
        client.disconnect()
# --- IBM stuff ends

@app.route('/',methods=['POST'])
def listen_and_play():
    data = json.loads(request.data)
    message = data['message']['text'].strip()
    print (message)
    username = data['message']['chat']['first_name']
    chat_id = data['message']['chat']['id']
    
    if chat_id in activeGames or message=='/start':
        if message == '/start':
            activeGames[chat_id] = Game(chat_id)
            requests.post(sendURL, data=json.dumps({"chat_id":chat_id, "text":"Hello {}! It's a new game. Start playing..".format(username)}), headers=headers)
            return "OK"
        
        game = activeGames[chat_id]
        
        try:
            guess = int(message)
        except ValueError:
            requests.post(sendURL, data=json.dumps({"chat_id":chat_id, "text":"Invalid input. Please send integers(for playing) or /start (for new game) only."}), headers=headers)
            return "OK"
        
        if game.isLive():
            result = game.play_turn(guess)
            if result not in ['won', 'lost']:
                requests.post(sendURL, data=json.dumps({"chat_id":chat_id, "text":"Nope, you should {0}. Remaining {1} attempt(s)".format(result, game.attempts+1)}), headers=headers)
                return "OK"
            else:
                if result == "won":
                    msg = "Congrats!"
                elif result == "lost":
                    msg = "The number was {}. Try harder next time.".format(game.num)
                full_msg = "You {0} after trying {1}. ".format(result, game.guesses) + msg
                requests.post(sendURL, data=json.dumps({"chat_id":chat_id, "text":full_msg}), headers=headers)
                return "OK"
        else:
            msg = "You {0} your last game (value = {2}) after trying {1}. Please send /start to begin playing a new game".format(game.status, game.guesses, game.num)
            requests.post(sendURL, data=json.dumps({"chat_id":chat_id, "text":msg}), headers=headers)
            return "OK"
    else:
        activeGames[chat_id] = "garbage value"
        requests.post(sendURL, data=json.dumps({"chat_id":chat_id, "text":"Hello {}, please send /start to begin a new game.".format(username)}), headers=headers)
        return "OK"

@app.route('/', methods=['GET'])
def homepage():
    return "GET requests are not supported. Go away."

port = int(os.getenv('PORT', 8000))
if __name__=='__main__':
    app.run(host='0.0.0.0', port=port)