# Importing the dependencies
import numpy as np
import pandas as pd
import datetime as dt

# SQL Alchemy and Flask
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflecting Database into ORM classes
Base = automap_base()

# Reflecting the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup....
#################################################

# Creating the Flask app
app = Flask(__name__)

#################################################
# Flask Routes....
#################################################

@app.route("/")
def homepage():
    return (
        f"Welcome to Surfs Up in Hawaii Climate API <br/> "
        f"************************************************<br/>"
        f"All Available Routes: <br/>"
        f"/api/v1.0/precipitation *** precipitation data for the latest year <br/>"
        f"/api/v1.0/stations *** all weather stations and observations <br/>"
        f"/api/v1.0/tobs *** temperature data for the latest year <br/>"
        f"************************************************<br/>"
        f"Date search (yyyy-mm-dd) <br/>"
        f"/api/v1.0/start date *** low, high, and average temp for date given and each date after<br/>"
        f"/api/v1.0/end date *** low, high, and average temp for date given and each date up to and including end date<br/>"
        f"************************************************<br/>"
    )
@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > "2010-01-01")
                      .order_by(Measurement.date)
                      .all())
    
    precipScore= []
    for result in results:
        precipDict = {result.date: result.prcp, "Station": result.station}
        precipScore.append(precipDict)

    return jsonify(precipScore)

@app.route("/api/v1.0/stations")
def stations():

    results = (session.query(Station.name).all())
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

