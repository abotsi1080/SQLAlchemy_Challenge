# Importing the dependencies
import numpy as np
import pandas as pd
import datetime as dt

# Importing SQL Alchemy toolkit and Object Relational Mapper (ORM)
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.pool import StaticPool

# Importing dependencies for threading
import queue
import threading

# Importing SQL Flask
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine to hawaii.sqlite
# I was having "sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 4513900032 and this is thread id 123145585844224." 
# I eventually found the following reference that addressed the threading error I was having
# "https://stackoverflow.com/questions/33055039/using-sqlalchemy-scoped-session-in-theading-thread"

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False}, poolclass=StaticPool, echo=True)

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
        f"/api/v1.0/date/2015-05-30 *** low, high, and average temp for date given and each date after<br/>"
        f"/api/v1.0/date/2015-05-30/2016-01-30 *** low, high, and average temp for date given and each date up to and including end date<br/>"
        
        f"************************************************<br/>"

        f" data available from 2010-01-01 to 2017-08-23 <br/>"
        
        f"************************************************<br/>"
        )

# Running the query results  for precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():

        # Converting the Query Results to a Dictionary 
        # Note: `date` is the Key and `prcp` is the Value
        # Calculating the Date for the previous year from the last data
        previousYear = dt.date(2017,8,23) - dt.timedelta(days=365)

        # Running a query to get the last 12 Months of precipitation daata 
        # With the `date` and `prcp` values only
        results = session.query(Measurement.date, Measurement.prcp)\
                .filter(Measurement.date >= previousYear)\
                .order_by(Measurement.date).all()
        # Converting the list of Tuples into a Dictionary
        precipScore = dict(results)
        # Returning JSON results of Dictionary
        return jsonify(precipScore)


# Running the query results for the stations
@app.route("/api/v1.0/stations")
def stations():

    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    # Returning JSON results 
    return jsonify(all_stations)


# Running the query results for the temperatures
@app.route("/api/v1.0/temperature")
def temperature():
        # Calculating the dates and temperature observations for the previous year from the last data
        previousYear = dt.date(2017,8,23) - dt.timedelta(days=365)

        # Running query to get the last 12 Months of precipitation Data 
        results = session.query(Measurement.date, Measurement.tobs)\
                .filter(Measurement.date >= previousYear)\
                .order_by(Measurement.date).all()
        # Converting list of Tuples into normal list
        tempObs = list(results)
        # Returning the JSON result of temperature observations (tobs) for the previous year
        return jsonify(tempObs)

# Running the query results for the start date
@app.route("/api/v1.0/<start>")
def start_day(start):
        start_day = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                .filter(Measurement.date >= start)\
                .group_by(Measurement.date).all()
        # Converting list of Tuples into normal list
        start_day_list = list(start_day)
        # Returning JSON list of Min Temp, Avg Temp and Max Temp for the Start
        return jsonify(start_day_list)

# Running the query results for the end date
@app.route("/api/v1.0/<start>/<end>")
def start_end_day(start, end):
        start_end_day = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                .filter(Measurement.date >= start)\
                .filter(Measurement.date <= end)\
                .group_by(Measurement.date).all()
        # Converting list of Tuples into normal list
        start_end_day_list = list(start_end_day)
        # Returning the+ JSON results of Min Temp, Avg Temp and Max Temp for the Start-End
        return jsonify(start_end_day_list)


if __name__ == "__main__":
    app.run(debug=True)