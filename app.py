from flask import Flask, jsonify, render_template, request, redirect, json
import sqlalchemy
import psycopg2
from sqlalchemy import create_engine
import json
#from flask_sqlalchemy import SQLAlchemy
import os
import model_randomforest
import seaborn as sns
import base64
from io import StringIO
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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
    cur.execute("SELECT countryname, indicatorname, cast(value as varchar(255) ) as value, target_groups FROM public.happiness_indicators_final;") 
    columns = [col[0] for col in cur.description]
    happiness_ind = [dict(zip(columns, row)) for row in cur.fetchall()]
    return jsonify(happiness_ind) 

    

@app.route("/api/happy-report")
def happyreport():
    cur.execute("SELECT country, cast(happiness_score_2015 as varchar(50)) as happiness_score_2015, happiness_rank_2015, cast(happiness_score_2016  as varchar(50)) as happiness_score_2016, happiness_rank_2016, cast(happiness_score_2017  as varchar(50)) as happiness_score_2017, happiness_rank_2017, cast(happiness_score_2018  as varchar(50)) as happiness_score_2018, happiness_rank_2018, cast(happiness_score_2019  as varchar(50)) as happiness_score_2019, happiness_rank_2019 FROM public.happiness_report;") 
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

    cur.execute("select CAST(\"0\" AS DECIMAL(6,5)) r_square from model_score;") 
    columns = [col[0] for col in cur.description]
    r_square = [dict(zip(columns, row)) for row in cur.fetchall()]
    print(r_square)
    
    return render_template("predict-happiness.html",predictor=predictor, columns=columns_data)
    #return render_template('predict-happiness-copy.html',  predictor=[data.to_html(classes='data')], columns=data.columns.values)

@app.route("/predict",methods=['GET', 'POST'])
def predict():
    if request.method == "POST":
        predictor_list = request.form.getlist('predictor')

        if(predictor_list):
            predictor_list = tuple(predictor_list)
        
            data = model_randomforest.predict(predictor_list)
            predictor=data['importances_html']
            model_score=data['model_score']
        

            img = BytesIO()
            clf_report=data['clf_report']
            sns_plot=sns.heatmap(clf_report.iloc[:-1, :].T, annot=True)
            plt.subplots_adjust(left=0.28)
            sns_plot.figure.savefig(img, format='png')
        
            plt.close()
            img.seek(0)

            plot_url = base64.b64encode(img.getvalue()).decode('utf8')
            print(plot_url)
        #return render_template('predict-happiness-copy.html',  predictor=[data.to_html(classes='table table-striped',header=['Predictors','Gini-importance'],index=True,border='', justify='unset')], columns=data.columns.values)
            return render_template('predict-happiness.html',  predictor=predictor, model_score=model_score,predictor_list=predictor_list, plot_url=plot_url)
        
      
    #data = model_randomforest.predict()    
 
    return redirect("/predict-happiness" , code=302)

@app.route("/happiness-map")
def happiness_map():

    return render_template("happiness-map.html")

@app.route("/happiness-indicators")
def happiness_indicators():

    return render_template("happiness-indicators.html")

@app.route("/country_plots")
def country_plots():

    return render_template("country_plots.html")

@app.route("/inference")
def inference():

    return render_template("inference.html")

@app.route("/model-in-action")
def model_in_action():

    return render_template("model-in-action.html")

    


if __name__ == "__main__":
    app.run(debug=True)