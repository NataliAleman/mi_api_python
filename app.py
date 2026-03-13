from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import threading
import json
import serial

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# --- configuration --------------------------------------------------------
# Database configuration:
# by default we use SQLite for simplicity, but you can switch to MySQL
# (the database name in your request is "rfid").
#
# To create the MySQL database and table, run these commands in the mysql shell:
#
#   CREATE DATABASE rfid;
#   USE rfid;
#   
#   CREATE TABLE cards (
#       id INT AUTO_INCREMENT PRIMARY KEY,
#       uid VARCHAR(128) NOT NULL UNIQUE,
#       owner VARCHAR(128),
#       access VARCHAR(256),
#       registered_at DATETIME,
#       created_at DATETIME DEFAULT CURRENT_TIMESTAMP
#   );
#
# install the pymysql driver (``pip install PyMySQL``) and set the URI below.
# Example URI:
#   mysql+pymysql://user:password@localhost/rfid
#
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/rfid'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# variable global para guardar la última tarjeta leída
ultimo_uid = None
# --------------------------------------------------------------------------

class Card(db.Model):
    __tablename__ = 'cards'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(128), nullable=False, unique=True)
    owner = db.Column(db.String(128), nullable=True)
    access = db.Column(db.String(256), nullable=True)
    registered_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'owner': self.owner or '',
            'access': self.access or '',
            'registered_at': self.registered_at.isoformat() if self.registered_at else None,
            'fecha': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# create the database tables if they don't exist
with app.app_context():
    db.create_all()

# serial port helper (runs in background reading to avoid blocking requests)
_serial = None
# to communicate between thread and endpoint
_last_uid = None


def start_serial_reader(port='COM4', baudrate=115200):
    global _serial, _last_uid
    try:
        _serial = serial.Serial(port, baudrate, timeout=1)
    except Exception as e:
        print('Error abriendo puerto serial:', e)
        _serial = None
        return

    def loop():
        global _last_uid
        while True:
            try:
                linea = _serial.readline().decode(errors='ignore').strip()
                if not linea:
                    continue
                # only attempt JSON parse if it looks like an object
                if not linea.startswith('{'):
                    # ignore garbage or non-json lines
                    # print('línea descartada:', repr(linea))
                    continue
                data = json.loads(linea)
                uid = data.get('uid')
                if uid:
                    print('Tarjeta leída (background):', uid)
                    _last_uid = uid  # store for scan endpoint
                    # save automatically if not exists within app context
                    with app.app_context():
                        if not Card.query.filter_by(uid=uid).first():
                            card = Card(uid=uid)
                            db.session.add(card)
                            db.session.commit()
                            print(f'insertado card id={card.id} uid={card.uid}')
            except json.JSONDecodeError:
                # ignore malformed json
                print('JSON inválido en lectura serial, descartado')
                continue
            except Exception as e:
                # log other serial errors
                print('Error en lectura serial:', e)
                pass

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()

# start reader when the app launches (non-blocking)
start_serial_reader()

@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/rfid')
def rfid():
    tarjetas = Card.query.order_by(Card.created_at.desc()).all()
    return render_template('rfid.html', tarjetas=tarjetas)

@app.route('/configurar-tarjeta', methods=['GET', 'POST'])
def configurar_tarjeta():
    if request.method == 'POST':
        card_id = request.form.get('card_id')
        owner = request.form.get('owner')
        access = request.form.get('access')
        registered = request.form.get('registered')
        card = Card.query.get(card_id)
        if card:
            card.owner = owner
            card.access = access
            if registered:
                try:
                    card.registered_at = datetime.fromisoformat(registered)
                except:
                    pass
            db.session.commit()
        return redirect(url_for('configurar_tarjeta'))
    cards = Card.query.order_by(Card.created_at.desc()).all()
    return render_template('configurar.html', cards=cards)


@app.route('/alta-tarjeta', methods=['GET', 'POST'])
def alta_tarjeta():
    if request.method == 'POST':
        uid = request.form.get('uid')
        owner = request.form.get('owner')
        access = request.form.get('access')
        registered = request.form.get('registered')
        if uid:
            existing = Card.query.filter_by(uid=uid).first()
            if not existing:
                card = Card(uid=uid, owner=owner or None, access=access or None)
                if registered:
                    try:
                        card.registered_at = datetime.fromisoformat(registered)
                    except:
                        pass
                db.session.add(card)
                db.session.commit()
        return redirect(url_for('alta_tarjeta'))
    return render_template('alta.html')

# API endpoints for AJAX
@app.route('/api/tarjetas')
def api_tarjetas():
    cards = Card.query.order_by(Card.created_at.desc()).all()
    return jsonify([c.to_dict() for c in cards])

@app.route('/api/scan', methods=['POST'])
def api_scan():
    # return the last UID read by background thread
    global _last_uid
    if _last_uid:
        uid = _last_uid
        _last_uid = None
        try:
            card = Card.query.filter_by(uid=uid).first()
            if not card:
                card = Card(uid=uid)
                db.session.add(card)
                db.session.commit()
                print(f'scan endpoint insert id={card.id} uid={card.uid}')
            # always return id as well
            card_id = card.id
        except Exception as e:
            print('Error guardando tarjeta en scan:', e)
            return jsonify({'success': False, 'message': 'error interno'}), 500
        return jsonify({'success': True, 'uid': uid, 'id': card_id})
    # if we got here, nothing new was read yet
    return jsonify({'success': False, 'message': 'No hay tarjeta nueva'}), 400

@app.route('/api/last-uid')
def api_last_uid():
    global _last_uid
    if _last_uid:
        # get the card to return id too
        card = Card.query.filter_by(uid=_last_uid).first()
        if card:
            return jsonify({'uid': _last_uid, 'id': card.id})
    return jsonify({'uid': None, 'id': None})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
