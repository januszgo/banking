from datetime import datetime
from flask import Flask, make_response, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, inspect, Table, Column, Integer, String, Float, MetaData
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://chmurowe:krkdbPch23!@chmurowedb.database.windows.net:1433/accountdb?driver=ODBC+Driver+17+for+SQL+Server"

db = SQLAlchemy(app)
eng = create_engine("mssql+pyodbc://chmurowe:krkdbPch23!@chmurowedb.database.windows.net:1433/accountdb?driver=ODBC+Driver+17+for+SQL+Server")
insp = inspect(eng)
accounts = insp.get_table_names()

@app.route('/', methods=['GET'])
def index():
    if request.args.get('toCreate') is not None and not inspect(eng).has_table(request.args.get('toCreate')):
        meta = MetaData()
        meta.reflect(bind=eng)
        meta.create_all(eng)
        accounts.append(request.args.get('toCreate'))
        accounts.sort()
    if request.args.get('toDelete') is not None and inspect(eng).has_table(request.args.get('toDelete')):
        meta = MetaData()
        meta.reflect(bind=eng)
        tab = meta.tables.get(request.args.get('toDelete'))
        meta.drop_all(bind=eng, tables=[tab])
        accounts.remove(request.args.get('toDelete'))        
    print('Request for index page received')
    return render_template('index.html', accounts = accounts)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/view', methods=['POST'])
def view():
    name = request.form.get('name')
    if name:
        print('Request for hello page received with name=%s' % name)
        #return render_template('hello.html', transactions = transactions, name = name)
        return render_template('hello.html', name = name)
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()