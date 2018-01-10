from flask import Flask, render_template, request, json
from flaskext.mysql import MySQL
import bcrypt

app = Flask(__name__)

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'appdb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 6666
mysql.init_app(app)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/hello')
def hello():
    return 'Hello, World'


@app.route('/signUp', methods=['POST'])
def signUp():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _email and _password:
            conn = mysql.connect()
            cursor = conn.cursor()
            # All Good, let's call MySQL
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(_password.encode('utf-8'), salt)
            cursor.callproc('new_user', (_email, hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message': 'User created successfully !'})
            else:
                return json.dumps({'error': str(data[0])})
        else:
            return json.dumps({'html': '<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


@app.route('/signIn', methods=['POST'])
def signIn():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _email and _password:
            conn = mysql.connect()
            cursor = conn.cursor()
            # All Good, let's call MySQL
            cursor.callproc('login_attempt', [_email])
            hashed_password = cursor.fetchall()[0][0]
            if bcrypt.checkpw(_password.encode('utf-8'), hashed_password):
                return "It Matches!"
            else:
                return "It Does not Match :("
        else:
            return json.dumps({'html': '<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    app.run()
