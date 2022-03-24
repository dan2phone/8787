import json, re
from flask import Flask, jsonify, Response, request, render_template
from flask_cors import CORS
import hacks

app = Flask(__name__)
CORS(app)

app.add_url_rule('/fire', view_func=hacks.fire)

status = 500

def updateDB(data):
    with open('store.json', 'w') as f:
        f.write(json.dumps(data))

def restoreCorruptDatabase():
    global data

    # Setting status to 205 signals that a database error has occured and that the database needed to reset
    status = 205

    data = {
        "numbers": [
            {
                "number": "+123456789",
                "valid": False,
            },
            {
                "number": "00237462389",
                "valid": True,
            },
        ],
        "creds": [
            {
                "username": "user",
                "password": "00000000",
            },
            {
                "username": "user",
                "password": "0000",
            },
            {
                "username": "admin",
                "password": "8888",
            }
        ]
    }

    updateDB(data)

def getCreds():
    global status

    try:
        status = 200
        response = data['creds']
    except (KeyError, TypeError):
        restoreCorruptDatabase()
        response = data['creds']

    return response

def getNumbers():
    global status

    try:
        status = 200
        response = data['numbers']
    except (KeyError, TypeError):
        restoreCorruptDatabase()
        response = data['numbers']

    return response

#########
# START #
#########

try:
    with open('store.json') as f:
        data = json.loads(f.read())
except json.decoder.JSONDecodeError:
    restoreCorruptDatabase()
    with open('store.json') as f:
        data = json.loads(f.read())

@app.route('/', methods = [ 'GET' ])
def homeview():
    return render_template('index.html')

@app.route('/numbers', methods = [ 'GET' ])
def numbers():
    return Response(json.dumps(getNumbers()), status=status, mimetype='application/json')

@app.route('/creds', methods = [ 'GET' ])
def creds():
    return Response(json.dumps(getCreds()), status=status, mimetype='application/json')

@app.route('/creds/<int:ix>', methods = [ 'DELETE' ])
def deleteCred(ix):
    global status
    try:
        del data['creds'][ix]
        
        status = 200
        updateDB(data)
    except KeyError:
        restoreCorruptDatabase()
    except ValueError:
        status = 404

    return Response(json.dumps(getCreds()), status=status, mimetype='application/json')

@app.route('/creds', methods = [ 'POST' ])
def addCred():
    global data
    global status

    try:
        cred = json.loads(request.data)

        if cred:
            data['creds'].append({
                'username': cred['username'],
                'password': cred['password']
            })

        updateDB(data)

        status = 200
    except json.decoder.JSONDecodeError:
        status = 400
    except KeyError:
        status = 400

    return Response(json.dumps(getCreds()), status=status, mimetype='application/json')

@app.route('/numbers', methods = [ 'POST' ])
def addNumber():
    global data
    global status

    try:
        num = json.loads(request.data)

        if num:
            data['numbers'].append({
                'number': num,
                'valid': bool(re.match('^[0-9]+$', num))
            })

        updateDB(data)

        status = 200
    except json.decoder.JSONDecodeError:
        status = 400

    return Response(json.dumps(getNumbers()), status=status, mimetype='application/json')
    #return Response(json.dumps(getNumbers()), status=status, mimetype='application/json')

@app.route('/numbers/<string:number>', methods = [ 'DELETE' ])
def deleteNumber(number):
    global status
    try:
        i = 0
        while i < len(data['numbers']):
            if data['numbers'][i]['number'] == number:
                del data['numbers'][i]
                break
            i+=1
        
        if i == len(data['numbers']):
            raise ValueError

        status = 200
        updateDB(data)

    except KeyError:
        restoreCorruptDatabase()
    except ValueError:
        status = 404

    return Response(json.dumps(getNumbers()), status=status, mimetype='application/json')

