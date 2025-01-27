

from flask import Flask, render_template, jsonify, request
from uuid import uuid4
from enum import Enum
from player import Player

#  Global
BOARD_SIZE = 5
MAX_PLAYER_COUNT = 2

app = Flask(__name__)

# Players
player_count = 0
PLAYER_UUIDS = {}
PLAYER_IDS = {}
players = []
waiting = 0
messages = []

# Landing
@app.route("/")
def index():
    return render_template("index.html")

# Team Info
@app.route('/submit-team-info', methods=['POST'])
def submit_team_info():
    global player_count
    try:
        # Get the JSON data from the request
        data = request.get_json()
        team_name = data.get('teamName')
        team_uuid = uuid4().hex
        cipher = data.get('cipher')

        if player_count >= MAX_PLAYER_COUNT:
            return jsonify({"message": "Max Player Reached!!!"}), 502
        
        # Player Initialization
        PLAYER_UUIDS[team_uuid] = player_count
        PLAYER_IDS[player_count] = team_uuid
        
        player_count += 1
        players.append(Player(BOARD_SIZE, team_name, cipher))

        # Log or process the received data
        print(f"Received Team Name: {team_name}, Cipher: {cipher}")
        return jsonify({"message": "Team info received successfully!", "teamName": team_name, "teamUUID": team_uuid, "cipher": cipher}), 200
    except Exception:
        return ({"message" : "Invaid team request"}), 502

# Ship Info
@app.route('/submit-ships', methods=['POST'])
def submit_ships():
    global waiting

    try:
        data = request.get_json()
        ships = data.get('ships', [])
        uuid = data.get('uuid')
    
        # Ship Initialization
        player_id = PLAYER_UUIDS[uuid]
        players[player_id].setShip(ships)
        waiting +=1
        players[player_id].state = State.WAIT_FOR_START.value
        check_wait()
        # Example: Save or process the ships
        print("Received ship layout:", ships)
        
        # Respond to the client
        return jsonify({"message": "Ship layout received!", "ships": ships}), 200
    except Exception:
        return ({"message" : "Invaid ship request"}), 502

# Get Messages
@app.route('/get-all-messages')
def get_moves():
    global messages
    return jsonify(messages)

# Get get-tables
CellStates = ["water", "ship", "attacked", "defended", "attacking"]

@app.route('/get-tables/<uuid>')
def get_tables(uuid):
    try:
        player_id = PLAYER_UUIDS[uuid]
    except Exception:
        return jsonify({"message": "Enter valid UUID"}),502
    user_table = []
    opponent_table = []
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            user_table.append({
                "x" : x,
                "y" : y,
                "color" : CellStates[int(players[player_id].my_board[x][y])]
            })
            opponent_table.append({
                "x" : x,
                "y" : y,
                "color" : CellStates[int(players[player_id].op_board[x][y])]
            })
    return jsonify({
        "table_data" : [user_table, opponent_table],
        "score" : players[player_id].points,
        "cipher" : players[player_id].cipher
    })

# Attack Phase
@app.route('/submit-attack', methods=['POST'])
def attack():
    global waiting
    global messages
    try:
        data = request.get_json()
        attack = data.get('attack')[0]
        uuid = data.get('uuid')
    
        player_id = PLAYER_UUIDS[uuid]
        if(players[player_id].state != State.ATTACK_STATE.value):
            return jsonify({"message": "Clicked multiple times :( refresh the page"}), 502
        players[player_id].state = State.WAIT_FOR_ATTACK.value

        print("Received attack:", attack)
        cmsg = "Attacked on " + players[player_id].encrypt((attack['x'],attack['y']))
        messages.append({"username" : players[player_id].team_name , "text" : cmsg})
        
        # players[player_id].attack = attack.x, attack.y
        players[player_id].setAttack(attack)
        
        waiting+=1
        check_wait()
        # Example: Save or process the ships
        # Respond to the client
        return jsonify({"message": "Attack received!", "attack": attack}), 200
    except Exception:
        return ({"message" : "Invaid attack request"}), 502

# Defend Phase
@app.route('/submit-defend', methods=['POST'])
def defend():
    global waiting
    global messsages
    try:
        data = request.get_json()
        defend = data.get('defend')[0]
        uuid = data.get('uuid')
        player_id = PLAYER_UUIDS[uuid]
        if(players[player_id].state != State.DEFEND_STATE.value):
            return jsonify({"message": "Clicked multiple times :( refresh the page"}), 502
        players[player_id].state = State.WAIT_FOR_DEFEND.value
        
        # Ship Initialization
        print("Received defense:", defend)
        
        cmsg = "Defended on " + players[player_id].encrypt((defend['x'],defend['y']))
        messages.append({"username" : players[player_id].team_name , "text" : cmsg})
        
        # players[player_id].defend = defend.x, defend.y
        players[player_id].setDefend(defend)
        
        waiting+=1
        check_wait()
        # Example: Save or process the ships
        
        # Respond to the client
        return jsonify({"message": "Defense received!", "defense": defend}), 200
    except Exception:
        return ({"message" : "Invaid defend request"}), 502

# State Management
class State(Enum):
    SELECT_ALGO_STATE = 0
    SELECT_SHIP_STATE = 1
    WAIT_FOR_START = 2
    ATTACK_STATE = 3
    WAIT_FOR_ATTACK = 4
    DEFEND_STATE = 5
    WAIT_FOR_DEFEND = 6
    WIN_STATE = 7
    LOSE_STATE = 8
    DRAW_STATE = 9

MOVE_WAIT_STATES = (State.WAIT_FOR_ATTACK.value, State.WAIT_FOR_DEFEND.value)
NUMBER_OF_STATES = 10

@app.route('/play/<uuid>')
def play(uuid):
    try:
        player_id = PLAYER_UUIDS[uuid]
    except Exception:
        return jsonify({"message": "Enter valid UUID"}),502
    cur_state = players[player_id].state
    if cur_state == State.SELECT_SHIP_STATE.value:
        return render_template('ship.html')
    elif cur_state == State.ATTACK_STATE.value:
        return render_template('attack.html')
    elif cur_state == State.DEFEND_STATE.value:
        return render_template('defend.html')
    elif cur_state in MOVE_WAIT_STATES:
        return render_template('wait_move.html')
    elif cur_state == State.WIN_STATE.value:
        return render_template('win.html')
    elif cur_state == State.LOSE_STATE.value:
        return render_template('lose.html')
    elif cur_state == State.DRAW_STATE.value:
        return render_template('draw.html')
    else:
        return render_template('wait_start.html')

def check_wait():
    global waiting
    global messages
    print("waiting : ",waiting)
    if waiting == 2:
        waiting = 0
        messages.append({"username" : "Admiral" , "text" : "Next Move"})
        for i in range(2):
            players[i].state += 1
            print("Player state changed to ", players[i].state)
            if(players[i].state == 7):
                players[i].updatePlayer(players[(i+1)%2])
                players[i].state = 3
        if(players[0].game_lost and players[0].game_lost):
            print("draw")
            players[0].state = players[1].state = 9
        elif(players[0].game_lost):
            print("player1 - win")
            players[0].state = 8
            players[1].state = 7
        elif(players[1].game_lost):
            print("player0 - win")
            players[0].state = 7
            players[1].state = 8

        for i in range(2):
            uuid = PLAYER_IDS[i]
            play(uuid) 

if __name__ == "__main__":
    app.run(debug=true)

@app.route('/get-score/<uuid>')
def getScore(uuid):
    try:
        player_id = PLAYER_UUIDS[uuid]
    except Exception:
        return jsonify({"message": "Enter valid UUID"}),502
    return jsonify({"score": players[player_id].score,"cipher" : players[player_id].cipher})

