# -*- coding: utf-8 -*-

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, jsonify
import json
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import os
from flask_cors import CORS
from hint_utils import HintService
from pandas import read_csv

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
cors = CORS(app, resources={r"/hint/*": {"origins": "*"}})
#db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
#funcrions
def generate_text(question, new_turn):
    #skinut' ' pastebin
    answer = ''
    if question[:16].lower() == 'какой лучший ход':
        best_move = new_turn['best_moves'][0]
        answer = ''
        answer = special_events(best_move['move', best_move['full_move']])
        if answer == '':
            answer = 'Предлагаю сходить ' + piece(best_move['move'][0], 't') + ' на ' + best_move['full_move'][1:3]
    print(answer)
    return answer

def who_on(cell):
    a = ord('a')
    board = state.split('/')
    for j in range(0, 8):
        for i in range(0, 9):
            board[j] = board[j].replace(str(i), '.' * i)
    # белые обозначаются большими буквами
    value = board[7 - (int(cell[1]) - 1)][ord(cell[0]) - a].upper()
    if value != '.':
        return value
    else:
        return 'Empty'

def special_events(string, full_move):
    result = ''
    if 'O-O-O' in string:
        result = 'Можно сделать рокировку с левой ладьей.'
    elif 'O-O' in string:
        result = 'Можно сделать рокировку с правой ладьей.'
    if '=' in string:
        result = 'Предлагаю превратить пешку на ' + string[:2] + ' в ' + piece(string[2], 'v') + '.'
    if 'x' in string:
        if piece(string[0], 't') == 'пешкой':
            result = 'Предлагаю ' + piece(string[0], 't') + ' съесть ' + piece(who_on(full_move[2:4]), 'v') + ' на ' + full_move[2:4] + '.'
    if '+' in string:
        if result[-1] == '.':
            result[-1] = ' '
            result = result + 'и поставить шах.'
        else:
            result = 'Можно поставить шах, сходив'
            p =  piece(string[0], 't')
            if p == 'пешкой':
                result = result + ' ' + p + ' на ' + string[:2] + '.'
            else:
                result = result + ' ' + p + ' на ' + string[1:3] + '.'
    if '#' in string:
        if result[-1] == '.':
            result[-1] = ' '
            result = result + 'и поставить мат.'
        else:
            result = 'Есть возможность поставить мат, сходив'
            p =  piece(string[0], 't')
            if p == 'пешкой':
                result = result + ' ' + p + ' на ' + string[:2] + '.'
            else:
                result = result + ' ' + p + ' на ' + string[1:3] + '.'
    return  result
def piece(char, case):
    pieces = {
        't': {
            'K' : 'королем',
            'Q' : 'ферзем',
            'R' : 'ладьей',
            'B' : 'слоном',
            'N' : 'конем'
        },
        'v' : {
            'K' : 'короля',
            'Q' : 'ферзя',
            'R' : 'ладью',
            'B' : 'слона',
            'N' : 'коня'
        }
    }
    pawn = {
        't' : 'пешкой',
        'v' : 'пешку'}
    if case in pieces:
        if char in pieces[case]:
            return pieces[case][char]
        else:
            return pawn[case]
    else:
        return ''

def json_answer(best_moves, possible_moves, answer, mate):
    return jsonify({
        'best_moves': best_moves,
        'possible_moves': possible_moves,
        'answer': answer,
        'mate': mate
    })

def get_answer(state):
    return {
    "possible_moves": [],
    "best_moves": [{
        "full_move": "f1e1",
        "mate": False,
        "move": "Re1",
        "score": 1.58
      }],
    "answer": "Если сходишь правильно, можешь поставить мат."
    }
    with open('game-temp.json') as f:
        game = json.load(f)
    if state in game:
        return game[state]
    else:
        return {
            "possible_moves": [],
            "best_moves": [],
            "answer": "ERROR!!!11 no such turn in test json"
        }



@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

state = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' # current board state
@app.route('/hint', methods=['POST'])
def hint():
    if request.method == 'POST':
        data = request.get_json()
        if not ('board' in data):
            return json_answer([], [], 'Error: no board information sent', False)
        state = data['board']
        question = data['question']

        csv = read_csv("data/dataset.tsv", sep='\t')
        hint = HintService(knowledge=csv, send_score=True)
        answer = hint.ask(question)

        # TODO: check board

        return json_answer([], [], answer, False)
    else:
        return json_answer([], [], 'Ошибка!', False)
# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port,debug=True)


