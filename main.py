# Author: Shehzad ul Islam - 1001555356

import os
from flask import Flask,redirect,render_template,request
import urllib
import datetime
import json
import ibm_db

app = Flask(__name__)

# get service information if on IBM Cloud Platform
if 'VCAP_SERVICES' in os.environ:
    db2info = json.loads(os.environ['VCAP_SERVICES'])['dashDB'][0]
    db2cred = db2info["credentials"]
    appenv = json.loads(os.environ['VCAP_APPLICATION'])
else:
    raise ValueError('Expected cloud environment')

def create_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        db2conn = ibm_db.connect("DATABASE="+db2cred['db']+";HOSTNAME="+db2cred['hostname']+";PORT="+str(db2cred['port'])+";UID="+db2cred['username']+";PWD="+db2cred['password']+";","","")
        return db2conn
    except:
        print("no connection:", ibm_db.conn_errormsg())
    else:
        print("The connection was successful")
    return None

# handle database request and query city information
def titanic(name=None):
    # connect to DB2
    db2conn = create_connection()
    if db2conn:
        # we have a Db2 connection, query the database
        # sql="select * from cities where name=? order by population desc"
        sql="select * from titanic"
        # parameter marker.
        stmt = ibm_db.prepare(db2conn,sql)        # Note that for security reasons we are preparing the statement first,
        # then bind the form input as value to the statement to replace the

        ibm_db.bind_param(stmt, 1, name)
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
    return render_template('titanic.html', collection=rows)

# main page to dump some environment information
@app.route('/')
def index():
    return render_template('index.html', app=appenv)

# for testing purposes - use name in URI
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/search', methods=['GET'])
def searchroute():
    name = request.args.get('name', '')
    return titanic(name)

@app.route('/titanic/<name>')
def titanicroute(name=None):
    return titanic(name)

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
