from flask import Flask, render_template, request, jsonify, session
import random
from flask import redirect, url_for
#from flask_session import Session

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
#session = Session(app)

# --- Game Logic Functions ---

def generate_board(n_row, n_col, num_mines):
    board = [[0 for _ in range(n_col)] for _ in range(n_row)]
    mines = set()

    while len(mines) < num_mines:
        r = random.randint(0, n_row - 1)
        c = random.randint(0, n_col - 1)
        if (r, c) not in mines:
            board[r][c] = 'X'
            mines.add((r, c))

    directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    for r in range(n_row):
        for c in range(n_col):
            if board[r][c] == 'X':
                continue
            count = 0
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n_row and 0 <= nc < n_col:
                    if board[nr][nc] == 'X':
                        count += 1
            board[r][c] = count
    return board, mines

def display_board(board):
    return [["#" for _ in row] for row in board]

def reveal_cell(board, covered_board, r, c):
    if covered_board[r][c] != "#":
        return True
    if board[r][c] == "X":
        covered_board[r][c] = "X"
        return False

    to_reveal = [(r, c)]
    directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    while to_reveal:
        x, y = to_reveal.pop()
        if covered_board[x][y] != "#":
            continue
        covered_board[x][y] = board[x][y]
        if board[x][y] == 0:
            for dr, dc in directions:
                nx, ny = x + dr, y + dc
                if 0 <= nx < len(board) and 0 <= ny < len(board[0]):
                    if covered_board[nx][ny] == "#":
                        to_reveal.append((nx, ny))
    return True

def flag_cell(covered_board, r, c):
    if covered_board[r][c] == "F":
        covered_board[r][c] = "#"
    elif covered_board[r][c] == "#":
        covered_board[r][c] = "F"
    return covered_board

def reveal_all_mines(board, covered_board):
    for r in range(len(board)):
        for c in range(len(board[0])):
            if board[r][c] == 'X':
                covered_board[r][c] = 'X'
    return covered_board

def check_win(board, covered_board, mine_coords):
    flagged = set()
    unrevealed = 0

    for r in range(len(covered_board)):
        for c in range(len(covered_board[0])):
            cell = covered_board[r][c]
            if cell == '#':
                unrevealed += 1
            elif cell == 'F':
                flagged.add((r, c))

    return flagged == mine_coords and unrevealed == 0

# --- Flask Routes ---

@app.route('/')
def index():
    if 'board' not in session:
        board, mines = generate_board(8, 10, 10)
        session['board'] = board
        session['covered'] = display_board(board)
        session['mines'] = list(mines)
        session['game_over'] = False

    return render_template("index.html", board=session['covered'])

@app.route('/action', methods=['POST'])
def action():
    data = request.get_json()
    r = data['row']
    c = data['col']
    button = data['button']

    board = session['board']
    covered = session['covered']
    mines = set(tuple(m) for m in session['mines'])

    if session.get('game_over', False):
        return jsonify({"board": covered, "game_over": True})

    if button == 'left':
        alive = reveal_cell(board, covered, r, c)
        if not alive:
            reveal_all_mines(board, covered)
            session['covered'] = covered
            session['game_over'] = True
            return jsonify({"board": covered, "game_over": True, "lost": True})
    elif button == 'right':
        flag_cell(covered, r, c)

    session['covered'] = covered

    if check_win(board, covered, mines):
        session['game_over'] = True
        return jsonify({"board": covered, "game_over": True, "won": True})

    return jsonify({"board": covered, "game_over": False})

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)
