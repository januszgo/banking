from datetime import datetime
from flask import Flask, make_response, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, inspect, Table, Column, Integer, String, Float, MetaData, select, insert, delete, update
from sqlalchemy.sql import functions
import os
import requests

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
        #meta.reflect(bind=eng)
        tab = Table(
        request.args.get('toCreate'), meta, 
        Column('id', Integer, primary_key = True), 
        Column('name', String), 
        Column('value', Float), 
        )
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

@app.route('/edit', methods=['POST'])
def edit():
    accountName = request.form.get('accountName')
    theId = request.form.get('theId')
    theName = request.form.get('theName')
    theValue = request.form.get('theValue')
    return render_template('edit.html', theId=theId, theName=theName, theValue=theValue, accountName=accountName)

@app.route('/view', methods=['POST'])
def view():
    tab_name = request.form.get('name')
    row_name = request.form.get('row_name')
    income = request.form.get('income')
    outcome = request.form.get('outcome')
    destination = request.form.get('destination')
    idToDelete = request.form.get('idToDelete')
    editedId = request.form.get('editedId')
    newName = request.form.get('newName')
    newValue = request.form.get('newValue')

    if tab_name is not None:
        meta = MetaData()
        #meta.reflect(bind=eng)
        #meta.create_all(eng)
        tab = Table(tab_name, meta,
            Column("id", Integer),
            Column("name", String(255)),
            Column("value", Float)
            )
        
        if editedId is not None and newName is not None and newValue is not None:
            newValue=round(float(newValue),2)
            connection = eng.connect()
            stmt = (
                update(tab).
                where(tab.columns.id==editedId).
                values(name=newName,value=newValue)
            )
            connection.execute(stmt)
            connection.commit()
            print('Request for spending received with name=' + str(row_name) + " value=" + str(outcome))

            
        if destination is not None and tab_name!=destination:
            outcome = float(outcome) * -1
            outcome = round(outcome,2)

            tab_dest = Table(destination, meta,
            Column("id", Integer),
            Column("name", String(255)),
            Column("value", Float)
            )
            stmt = (
                insert(tab).
                values(name="Przelew do " + destination, value=outcome)
            )
            connection = eng.connect()
            connection.execute(stmt)
            stmt = (
                insert(tab_dest).
                values(name="Przelew od " + tab_name, value=outcome * -1)
            )
            connection.execute(stmt)
            connection.commit()
            print('Request for transfer from' + tab_name + 'to' + destination + " value=" + str(income))
        
        if outcome is not None and destination is None:
            outcome = float(outcome) * -1
            outcome = round(outcome,2)

            stmt = (
                insert(tab).
                values(name=row_name, value=outcome)
            )
            connection = eng.connect()
            connection.execute(stmt)
            connection.commit()
            print('Request for spending received with name=' + str(row_name) + " value=" + str(outcome))

        if income is not None:
            income = float(income)
            income = round(income,2)
            stmt = (
                insert(tab).
                values(name=row_name, value=income)
            )
            connection = eng.connect()
            connection.execute(stmt)
            connection.commit()
            print('Request for income received with name=' + str(row_name) + " value=" + str(income))

        if idToDelete is not None:
            stmt = (
                delete(tab).
                where(tab.columns.id==idToDelete)
            )
            connection = eng.connect()
            connection.execute(stmt)
            connection.commit()
            print('Request for delete for element with id=' + str(id))

        stmt = select(
            tab.columns.id,
            tab.columns.name,
            tab.columns.value
        )
        connection = eng.connect()
        res = connection.execute(stmt).fetchall()

        print('Request for account balance received with name=%s' % tab_name)
        #return render_template('hello.html', transactions = transactions, name = name)

        stmt = select(
            functions.sum(tab.columns.value)
        )
        connection = eng.connect()
        balance = connection.execute(stmt).fetchall()[0][0]
        if balance is not None:
            balance = round(balance,2)
        else:
            balance = 0.00

        response = requests.get("https://api.exchangerate.host/latest")
        plneur=1/response.json()['rates']['PLN']
        plneur = round(plneur,2)

        return render_template('view.html', res=res, name=tab_name, accounts=accounts, balance=balance, plneur=plneur)
    else:
        print('Request for account balance received with no name or blank name -- redirecting')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()