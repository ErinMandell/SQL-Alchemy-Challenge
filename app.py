# Imports
#-----------------------------------------------

import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# ------------------------------------------------
# Database Setup
#-------------------------------------------------
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


# ------------------------------------------------------
# Flask Setup
#------------------------------------------------------
app = Flask(__name__)

# Index Route
@app.route("/")
def welcome():
    return (
        f"Welcome to my Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br>"
        f"/api/v1.0/temp/start/end"
    )


# Precipitation Data Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    last_date = session.query(func.max(Measurement.date)).first()

    for x in last_date:
        parts = x.split("-")
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])

    begin_date = dt.date(year,month,day) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    year_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= begin_date).all()

    # Print dictionary with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in year_data}
    return jsonify(precip)



# Most Active Weather Stations Route
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    most_active = session.query(Station.station).all()

    # Unravel the station data into an array and convert to a list
    stations = list(np.ravel(most_active))
    return jsonify(stations)


# Temperature Observations Route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    
    # Calculate the date 1 year ago from last date in database
    last_date = session.query(func.max(Measurement.date)).first()

    for x in last_date:
        parts = x.split("-")
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
    begin_date = dt.date(year,month,day) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
    temp_results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= begin_date).all()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(temp_results))

    # Return the results
    return jsonify(temps)


# Display Min, Max, and Avg temperature recorded during my vacation

 # Note: I GET NULL VALUES RETURNED IN THE BROWSER, AND I DON'T KNOW WHY ...
 # THIS CODE RUNS WITHOUT ERROR IN JUPYTER NOTEBOOK, SO I'M NOT SURE WHAT'S GOING ON HERE.

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start='2012-02-01', end='2012-02-14'):
    
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        final_results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(final_results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    final_results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(final_results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run()