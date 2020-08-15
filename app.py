from flask import Flask, jsonify, render_template, request, redirect, json
import sqlalchemy
import psycopg2
from sqlalchemy import create_engine
import json
#from flask_sqlalchemy import SQLAlchemy
import os
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

from urllib.parse import urlparse

print(os.environ.get("DATABASE_URL"))


#os.environ["DATABASE_URL"] = "postgres://fbcshsxigvoylt:10631d0d80106f558fa5dd4ba0c8aa0a0bdc227020cd09f7bfae6e75ec3fd4e8@ec2-3-215-207-12.compute-1.amazonaws.com:5432/de5fjc5oru29o5"

if "DATABASE_URL" in os.environ :
    url = urlparse(os.environ.get('DATABASE_URL'))
    db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
    schema = "schema.sql"
    conn = psycopg2.connect(db)
    #cur = conn.cursor()
else: 
    conn = psycopg2.connect(host="localhost", port = 5432, database="world_happiness")

print(conn)

#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL") or 'postgres://swain:db@localhost/Minneapolis_Police_Force_db'
#print(app.config['SQLALCHEMY_DATABASE_URI'])

#engine = create_engine(f'postgresql://swain:db@localhost:5432/Minneapolis_Police_Force_db')
#connection = engine.connect()
# Create a cursor object


cur = conn.cursor()
# engine = psycopg2.connect("postgresql://postgres:postgres@localhost:52632/mydatabase", echo=False)
#################################################
# Flask Routes
#################################################
#pd.read_sql


@app.route("/")
def echo():
        

    return render_template("index.html")

@app.route("/api/happiness-indicators")
def happinessindicators():
    cur.execute("select * from happiness_indicators_final") 
    columns = [col[0] for col in cur.description]
    happiness_ind = [dict(zip(columns, row)) for row in cur.fetchall()]
    return jsonify(happiness_ind) 

    

@app.route("/api/happy-report")
def happyreport():
    cur.execute("select * from happiness_report;") 
    columns = [col[0] for col in cur.description]
    happy_rpt = [dict(zip(columns, row)) for row in cur.fetchall()]
    return jsonify(happy_rpt) 



if __name__ == "__main__":
    app.run(debug=True)