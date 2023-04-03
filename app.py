from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, inspect, Table, Column, Integer, String, Float, MetaData
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://chmurowe:krkdbPch23!@chmurowedb.database.windows.net:1433/accountdb?driver=ODBC+Driver+17+for+SQL+Server"

db = SQLAlchemy(app)
eng = create_engine("mssql+pyodbc://chmurowe:krkdbPch23!@chmurowedb.database.windows.net:1433/accountdb?driver=ODBC+Driver+17+for+SQL+Server")
insp = inspect(eng)
accounts = insp.get_table_names()
meta = MetaData()

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    value = db.Column(db.Double)

@app.route('/', methods=['GET'])
def index():
    if request.args.get('name') is not None and not inspect(eng).has_table(request.args.get('name')):
        nt = Table(
        request.args.get('name'), meta, 
        Column('id', Integer, primary_key=True), 
        Column('name', String(255)), 
        Column('value', Float),
        )
        meta.create_all(eng)
        accounts.append(request.args.get('name'))
        accounts.sort()
        
    print('Request for index page received')
    return render_template('index.html', accounts = accounts)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()