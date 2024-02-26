from flask import Flask, redirect, render_template, request
import sqlite3
from random import randint, choice, shuffle
import requests
import os

app = Flask(__name__)

head = r'''<!-- Required meta tags -->
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

  <style>
    .btn {
      padding: 1px 6px;
      border: 1px outset buttonborder;
      border-radius: 0px;
      color: #FFFFFF;
      background-color: #8E2F2F;
      text-decoration: none;
    }
  </style>
  '''


def req_sql(cmd, vals=None):
    conn = sqlite3.connect('flask.db')
    c = conn.cursor()
    if vals is not None:
        res = c.execute(cmd, vals).fetchall()
    else:
        res = c.execute(cmd).fetchall()
    conn.commit()
    conn.close()
    return res


req_sql("""CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)""")

req_sql("""CREATE TABLE IF NOT EXISTS decks (
    deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_name TEXT NOT NULL,
    username TEXT NOT NULL
)""")

req_sql("""CREATE TABLE IF NOT EXISTS cards (
    card_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lemma TEXT NOT NULL,
    deck_id TEXT NOT NULL,
    mastery INTEGER DEFAULT 0
)""")


def get_form(card):
    response = requests.get(
        f'http://api.tezaurs.lv/v1/inflections/{card["lemma"]}')
    paradigm = response.json()[0]
    forms = [
        form['Vārds'] for form in paradigm
        if form.get('Vārdšķira') == 'Darbības vārds' and form.get('Laiks') ==
        card['laiks'] and form.get('Persona') == card['persona']
        and form.get('Skaitlis') in (card['skaitlis'], 'Nepiemīt') and
        form.get('Izteiksme') == 'Īstenības' and form.get('Noliegums') == 'Nē'
    ]
    return forms


def check_verb(word):
    response = requests.get(f'http://api.tezaurs.lv/v1/inflections/{word}')
    if response.status_code == 200:
        paradigm = response.json()[0]
        verbs = [
            form for form in paradigm
            if form.get('Vārdšķira') == 'Darbības vārds'
        ]
        if len(verbs) > 0:
            return True
        else:
            return False
    else:
        print('response error', response.status_code)


username = None
password = None
cards = []


def not_in_deck(lemma, deck_id):
    cards = req_sql('SELECT * FROM cards WHERE lemma = ? AND deck_id = ?',
                    (lemma, deck_id))
    if len(cards) == 0:
        return True
    else:
        return False


def add_default_decks(username):
    for file in os.listdir('default_decks'):
        deck_name = file.split('.')[0]
        req_sql('INSERT INTO decks (deck_name, username) VALUES (?, ?)',
                (deck_name, username))
        deck_id = req_sql(
            'SELECT deck_id FROM decks WHERE deck_name = ? AND username = ?',
            (deck_name, username))[0][0]
        with open(f'default_decks/{file}', 'r') as f:
            words = f.read().split('\n')
            for word in words:
                req_sql('INSERT INTO cards (lemma, deck_id) VALUES (?, ?)',
                        (word, deck_id))


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global username
    global password
    username = request.form['username']
    password = request.form['password']
    res = req_sql("SELECT * FROM users WHERE username=? AND password=?",
                  (username, password))
    if len(res) == 1:
        return redirect('/dashboard')
    else:
        return redirect('/')


@app.route('/new_user')
def new_user():
    return render_template('new_user.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global username
    global password
    username = request.form['username']
    password = request.form['password']

    req_sql("INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password))
    add_default_decks(username)

    return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    if (username is None) or (password is None):
        return redirect('/')
    else:
        decks = req_sql(
            'SELECT deck_id, deck_name FROM decks WHERE username=?',
            (username, ))
        return render_template('dashboard.html',
                               head=head,
                               username=username,
                               decks=decks)


@app.route('/new_deck')
def new_deck():
    if (username is None) or (password is None):
        return redirect('/')
    else:
        return render_template('new_deck.html', head=head, username=username)


@app.route('/deck_created', methods=['GET', 'POST'])
def deck_created():
    if (username is None) or (password is None):
        return redirect('/')
    else:
        deck_name = request.form['deck_name']
        req_sql("INSERT INTO decks (deck_name, username) VALUES (?, ?)",
                (deck_name, username))
        return redirect('/dashboard')


@app.route('/new_card')
def new_card():
    decks = req_sql("SELECT deck_id, deck_name FROM decks WHERE username=?",
                    (username, ))
    return render_template('new_card.html',
                           head=head,
                           username=username,
                           decks=decks)


@app.route('/card_created', methods=['GET', 'POST'])
def card_created():
    if (username is None) or (password is None):
        return redirect('/')
    else:
        lemma = request.form['lemma']
        deck_id = request.form['deck_id']
        if check_verb(lemma) and not_in_deck(lemma, deck_id):
            req_sql("INSERT INTO cards (lemma, deck_id) VALUES (?, ?)",
                    (lemma, deck_id))
            return redirect('/dashboard')
        else:
            return redirect('/wrong_word')


@app.route('/wrong_word')
def wrong_word():
    return render_template('wrong_word.html')


@app.route('/study/<deck>', methods=['GET', 'POST'])
def study(deck):
    if (username is None) or (password is None):
        return redirect('/')
    else:
        global cards
        if len(cards) == 0:  # if the study session is not started yet
            cards_raw = req_sql(
                "SELECT card_id, lemma, mastery FROM cards WHERE cards.deck_id = ? ORDER BY mastery ASC LIMIT 15",
                (deck, ))
            shuffle(cards_raw)
            for card in cards_raw:
                card_fine = {
                    'card_id': card[0],
                    'lemma': card[1],
                    'mastery': card[2],
                    'laiks': choice(('Pagātne', 'Tagadne', 'Nākotne')),
                    'persona': choice(('1', '2', '3')),
                    'skaitlis': choice(('Vienskaitlis', 'Daudzskaitlis')),
                }
                card_fine['form'] = get_form(card_fine)
                cards.append(card_fine)

        if 'guess' in request.form and os.environ.get(
                "WERKZEUG_RUN_MAIN") == "true":
            # if not the first card in the session
            guess = request.form['guess']
            if guess in cards[0]['form']:
                # if the guess of the previous card  is correct:
                output = f'Pareizi! {cards[0]["lemma"]} => {guess}'
                output_color = 'green'
                # increase mastery and remove the card from study session
                req_sql("UPDATE cards SET mastery = ? WHERE card_id = ?",
                        (cards[0]['mastery'] + 1, cards[0]['card_id']))
                cards.pop(0)
            else:
                output = f'Aplami! {cards[0]["lemma"]} => {cards[0]["form"][0]}, nevis {guess}'
                output_color = 'red'
                # increase mastery and move the card to the end of study session
                req_sql("UPDATE cards SET mastery = ? WHERE card_id = ?",
                        (cards[0]['mastery'] - 2, cards[0]['card_id']))
                cards.append(cards.pop(0))
        else:
            output = ''
            output_color = 'black'

        if len(cards) > 0:
            return render_template('study.html',
                                   head=head,
                                   username=username,
                                   card=cards[0],
                                   output=output,
                                   output_color=output_color,
                                   deck=deck)
        else:
            return render_template('study_over.html',
                                   head=head,
                                   username=username,
                                   output=output,
                                   output_color=output_color,
                                   deck=deck)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
