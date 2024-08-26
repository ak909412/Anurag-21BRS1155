from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Game State
game_state = {
    "board": [["", "", "", "", ""] for _ in range(5)],
    "players": {
        "A": {"P1": (0, 0), "H1": (0, 1), "H2": (0, 2)},
        "B": {"P1": (4, 0), "H1": (4, 1), "H2": (4, 2)}
    },
    "turn": "A"
}

def validate_move(player, piece, move):
    # Example logic to validate moves based on game rules
    current_pos = game_state['players'][player][piece]
    row, col = current_pos
    if move == 'L':
        new_pos = (row, col - 1)
    elif move == 'R':
        new_pos = (row, col + 1)
    elif move == 'F':
        new_pos = (row - 1, col) if player == 'A' else (row + 1, col)
    elif move == 'B':
        new_pos = (row + 1, col) if player == 'A' else (row - 1, col)
    elif move in ['FL', 'FR', 'BL', 'BR'] and piece.startswith('H2'):
        new_pos = move_hero2(move, row, col, player)
    else:
        return False

    # Check bounds and if new position is valid
    if 0 <= new_pos[0] < 5 and 0 <= new_pos[1] < 5:
        game_state['players'][player][piece] = new_pos
        return True
    return False

def move_hero2(move, row, col, player):
    # Handle diagonal movements for Hero2
    if move == 'FL':
        return (row - 2, col - 2) if player == 'A' else (row + 2, col + 2)
    elif move == 'FR':
        return (row - 2, col + 2) if player == 'A' else (row + 2, col - 2)
    elif move == 'BL':
        return (row + 2, col - 2) if player == 'A' else (row - 2, col + 2)
    elif move == 'BR':
        return (row + 2, col + 2) if player == 'A' else (row - 2, col - 2)

@socketio.on('move')
def handle_move(data):
    player = game_state['turn']
    piece = data['piece']
    move = data['move']

    if validate_move(player, piece, move):
        emit('update', game_state, broadcast=True)
        game_state['turn'] = 'B' if game_state['turn'] == 'A' else 'A'

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
