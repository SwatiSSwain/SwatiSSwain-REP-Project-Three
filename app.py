from flask import Flask, jsonify, render_template, request, redirect, json
import sqlalchemy
import psycopg2
from sqlalchemy import create_engine
import json
#from flask_sqlalchemy import SQLAlchemy
import os
import model_randomforest
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

from urllib.parse import urlparse

print(os.environ.get("DATABASE_URL"))


os.environ["DATABASE_URL"] = "postgres://sxwlsbsllohawb:4723d0dab89d2da6bf1aae12930fd6865874a185e4e4dca60e5af580ccd1a185@ec2-52-200-48-116.compute-1.amazonaws.com:5432/d7shhrp5hdjs4d"

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

@app.route("/predict-happiness")
def predict_hp():

    #Column names for table in prediction
    columns_data = ['Predictors','Gini-Importance' ]

    #Query table 
    cur.execute("select index, CAST(\"Gini-importance\" AS DECIMAL(5,4)) gini_importance from forest_importance order by CAST(\"Gini-importance\" AS DECIMAL(5,4)) desc;")
    predictor = cur.fetchall()

    #Column names for table in prediction
    #columns_data2 = ['R-Square' ]

    #Query table 
    #cur.execute("select CAST(\"0\" AS DECIMAL(6,5)) r_square from model_score;")
    #r_square = cur.fetchall()

    #cur.execute("select CAST(\"0\" AS DECIMAL(6,5)) r_square from model_score;") 
    #columns = [col[0] for col in cur.description]
    #r_square = [dict(zip(columns, row)) for row in cur.fetchall()]
    
    return render_template("predict-happiness.html",predictor=predictor, columns=columns_data)

@app.route("/predict")
def predict():
    data = model_randomforest.predict()    
 
    return redirect("/predict-happiness", code=302)



if __name__ == "__main__":
    app.run(debug=True)